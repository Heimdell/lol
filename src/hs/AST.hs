
{-# LANGUAGE TypeSynonymInstances #-}
{-# LANGUAGE FlexibleInstances #-}

import Control.Arrow hiding (app, )
import Control.Monad.State
import Control.Monad.Reader
import Control.Monad.Except
import Control.Monad.Writer.Strict

import Data.List

import Debug.Trace

test = foldl (flip apply) ast ss
  where
    Right ss = runExceptT (solve ts) `evalState` 0

    (Right _, (_, ts)) = eqs

    eqs = runTypeRefinement [] 
        $ equations 
        $ ast

    ast = let_ 
            [ be "id  x" (Hole "ID")  (app [var "x"])
            ] 
            (app [var "id"])
      -- let id x = x in id 1

let_ = Let ()
be x = Binding () name args
  where
    name : args = words x

app (f : xs) = App () f xs
var          = Var ()
c            = Const ()

data AST
    = Let Info [Binding] AST
    | App Info Term [Term]
    deriving (Show, Eq)

data Term
    = Var   Info String
    | Const Info String
    deriving (Show, Eq)

data Binding = Binding Info Name [Name] Type AST
    deriving (Show, Eq)

type Name = String

type Info = ()

data Type
    = Hole Name
    | Ground Name
    | Arrow Type Type
    | Forall [Name] Type
    deriving (Show, Eq)

type Environment = [(Name, Type)]

type TypeRefinement = ExceptT String (ReaderT Environment (State (Int, [(Type, Type)])))

runTypeRefinement :: Environment -> TypeRefinement a -> (Either String a, (Int, [(Type, Type)]))
runTypeRefinement env
    = (`runState`   (0, []))
    . (`runReaderT` env)
    .   runExceptT

class Refinable r where
    equations :: r -> TypeRefinement Type

instance Refinable AST where
    equations ast = do
        case ast of
            Let _ bindings context -> do
                let forwarded = flip map bindings $ \(Binding () n _ t _) -> (n, t)
                local (forwarded ++) $ do
                    forM_ bindings equations
                    equations context

            App _ f xs -> do
                txs  <- forM xs $ \x -> do
                    t <- equations x
                    return (x, t)

                root <- equations f
                foldM aux root (reverse txs)
              where
                aux tf (x, tx) = do
                    tr <- fresh
                    modify $ second ((tf, Arrow tx tr) :)
                    return tr

instance Refinable Term where
    equations term = do
        case term of
            Var info name -> do
                env <- ask
                case lookup name env of
                    Nothing -> 
                        throwError ("undefined " ++ name ++ "@" ++ show info)
                    
                    Just t -> do
                        return t

            Const info it -> do
                return (Ground "*")


instance Refinable Binding where
    equations (Binding info name args ty body) = do
        delta <- forM args $ \arg -> do
            t <- fresh
            return (arg, t)

        r <- local (delta ++) $ do
            equations body

        t <- foldM aux r (reverse delta)
        t <- generalize t

        modify $ second ((ty, t) :)

        return (Ground "?")

      where
        aux r (x, tx) = return (Arrow tx r)

fresh :: TypeRefinement Type
fresh = do
    modify $ first (+1)
    (num, _) <- get
    return (Hole (show num ++ "?"))

typeVars (Hole name)   = [name]
typeVars (Ground _)    = []
typeVars (Arrow l r)   = typeVars l ++ typeVars r
typeVars (Forall ns x) = typeVars x \\ ns

uses tname t = tname `elem` typeVars t

generalize :: Type -> TypeRefinement Type
generalize t = do
    env     <- ask
    (_, ss) <- get

    let fullEnv   = map snd env ++ map snd ss

    let tv        = typeVars t
    let inUse var = any (uses var) fullEnv
    let free      = nub $ filter (not . inUse) tv

    return (Forall free t)

class Appliable a where
    apply :: (Name, Type) -> a -> a

instance Appliable Type where
    apply (n, t) ty = case ty of
        Hole n' | n == n' -> t
        Arrow l r         -> apply (n, t) l `Arrow` apply (n, t) r
        Forall names x
            | n `notElem` names -> Forall names (apply (n, t) x)
        otherwise         -> ty

instance Appliable Environment where
    apply = (:)

instance Appliable [(Type, Type)] where
    apply s = map (apply s *** apply s)

instance Appliable AST where
    apply s (Let i bs context) = Let i (map (apply s) bs) (apply s context)
    apply s (App i f  xs)      = App i f xs

instance Appliable Binding where
    apply s (Binding i n az t body) = Binding i n az (apply s t) body

solve :: [(Type, Type)] -> ExceptT String (State Int) [(Name, Type)]
solve equations = case equations of
    [] -> 
        return []
    ((l, r) : rest) 
        | l == r ->
            solve rest

    ((Hole name, t) : rest)
        | not $ uses name t ->
            ((name, t) :) `fmap` solve (apply (name, t) rest)

        | otherwise ->
            throwError $ "cyclic type: " ++ show (Hole name, t)

    ((t, Hole name) : rest)
        | not $ uses name t ->
            ((name, t) :) `fmap` solve (apply (name, t) rest)

        | otherwise ->
            throwError $ "cyclic type: " ++ show (Hole name, t)

    ((x, Forall names' x') : rest) -> do
        y' <- foldM aux x' names'

        solve ((x, y') : rest)

    ((Forall names x, x') : rest) -> do
        y  <- foldM aux x names
        solve ((y, x') : rest)

    ((Arrow l r, Arrow l' r') : rest) -> do
        solve ((r, r') : (l', l) : rest)

    ((Ground n, Ground n') : rest)
        | n == n' -> do
            solve rest

    other ->
        throwError $ "no match: " ++ show (head equations)
  where
    aux body n = do
        m <- freshName
        return (apply (n, m) body)

freshName = do
    modify (+ 1)
    n <- get
    return (Hole (show n ++ "!"))