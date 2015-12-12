{-# LANGUAGE TypeSynonymInstances #-}
{-# LANGUAGE FlexibleInstances    #-}

import Control.Monad.State
import Control.Monad.Reader
import Control.Monad.Except

import qualified Data.Set as Set
import           Data.Set   (Set, member, singleton, (\\))

import qualified Data.Map as Map
import           Data.Map   (Map)

import Data.Monoid ((<>))

import Control.Applicative hiding (Const)
import Data.Char
import Text.ParserCombinators.ReadP hiding (get, many)

{-
    Type inference, adopted from algorithm W (Damas-Milner) and my previous
    experience.
-}

{-
    AST is in the ANF form - allowed constructs are only:
      - let-bindings (func/value decls)
      - application of terminals
-}

data AST
    = Let [Binding] AST
    | App Term [Term]
    deriving (Show, Eq)

data Term
    = Var   Name
    | Const String
    deriving (Show, Eq)

data Binding
    = Binding Name [Name] QType AST
    deriving (Show, Eq)

type Name = String

data Type
    = Hole Name
    | Ground Name
    | Type :=> Type 
    deriving (Show, Eq)

data QType
    = Forall (Set Name) Type
    deriving (Show, Eq)

newtype Substitution = Substitution { fromSubstitution :: [(Name, Type)] }
    deriving (Show, Eq)

(=:) :: Name -> Type -> Substitution
(=:) = curry (Substitution . (:[]))

type Environment = Map Name QType

(=:=) :: Name -> QType -> Environment
(=:=) = curry (Map.fromList . (:[]))

instance Monoid Substitution where
    mempty = Substitution mempty
    mappend (Substitution l) (Substitution r) =
        Substitution (l <> r)

class WithTypes wt where
    freeTypeVars :: wt -> Set Name
    applyOne     :: (Name, Type) -> wt -> wt

apply :: WithTypes wt => Substitution -> wt -> wt
apply (Substitution list) x = foldl (flip applyOne) x list

instance WithTypes Substitution where
    freeTypeVars = mconcat . map (freeTypeVars . snd) . fromSubstitution
    applyOne s   = Substitution . (s :) . fromSubstitution

instance WithTypes Type where
    freeTypeVars (Hole n)   = singleton n
    freeTypeVars (d :=> i)  = freeTypeVars d <> freeTypeVars i
    freeTypeVars (Ground _) = mempty

    (n, t) `applyOne` Hole m | n == m = t
    s      `applyOne` (dom :=> img)   = applyOne s dom :=> applyOne s img
    _      `applyOne` other           = other

instance WithTypes AST where
    freeTypeVars (Let bs context) = freeTypeVars bs <> freeTypeVars context

    s `applyOne` Let bs context = Let (applyOne s bs) (applyOne s context)
    _ `applyOne` App f  xs      = App f xs

instance WithTypes a => WithTypes [a] where
    freeTypeVars = mconcat . map freeTypeVars
    applyOne     = map . applyOne

instance WithTypes Binding where
    freeTypeVars (Binding _ _ ty _)        = freeTypeVars ty
    s `applyOne` Binding name args ty body = Binding name args (applyOne s ty) body

instance WithTypes QType where
    freeTypeVars (Forall names ty) = freeTypeVars ty \\ names

    s@(n, _) `applyOne` qt@(Forall names ty)
        | n `elem` names = qt
        | otherwise      = Forall names (applyOne s ty)

instance WithTypes Environment where
    freeTypeVars = mconcat . map freeTypeVars . Map.elems
    applyOne     = Map.map . applyOne

generalize :: Type -> TypeInference QType
generalize t = do
    env <- ask
    return (Forall (free env) t)
  where
    free env = freeTypeVars t \\ freeTypeVars env

type TypeInference = ExceptT String (ReaderT Environment (State Int))

runTypeInference :: TypeInference a -> Either String a
runTypeInference = runTypeInferenceKnowing mempty

runTypeInferenceKnowing knowledge 
    = (`evalState` 0)
    . (`runReaderT` knowledge)
    . runExceptT

fresh :: TypeInference Type
-- make a fresh type variable
fresh = do
    number <- get
    modify (+1)
    return $ Hole (show number <> "?")

instantiate :: QType -> TypeInference Type
-- generate a fresh binding for each forall-bound variable
instantiate (Forall names ty) = do
    let names' = Set.toList names
    list <- forM names' $ \name -> do
        ty <- fresh
        return (name, ty)

    return (apply (Substitution list) ty)

unify :: Type -> Type -> TypeInference Substitution
unify (a :=> b) (c :=> d) = do
    s1 <- unify a c
    s2 <- unify (apply s1 b) (apply s1 d)
    return (s1 <> s2)

unify (Hole a) b = bindVar a b
unify a (Hole b) = bindVar b a
unify (Ground _) (Ground _) = return mempty
unify x y = throwError $ show x <> "~/~" <> show y

bindVar :: Name -> Type -> TypeInference Substitution
bindVar name ty
    -- each var is equal to itself
    | ty == Hole name
        = return mempty
    | name `member` freeTypeVars ty 
        = die ["cycle in type: ", name, " = ", show ty]
    | otherwise
        = return (Substitution [(name, ty)])

{-
    The main interface for typing. For any Inferrable, generate
    substitutions, type and a new representation.
-}
class Inferrable i where
    infer :: i -> TypeInference (Substitution, Type, i)

instance Inferrable Term where
    infer (Var name) = do
        t <- lookupAtEnv name
        return (mempty, t, Var name)

    infer (Const x) = do
        return (mempty, Ground "*", Const x)

lookupAtEnv :: Name -> TypeInference Type
lookupAtEnv name = do
    env <- ask
    t <- maybe (die ["what is ", name, "?"])
     return (Map.lookup name env)

    instantiate t

die :: [String] -> TypeInference a
die = throwError . concat

instance Inferrable AST where
    infer (App f xs) = do
        tresult <- fresh
        pile    <- mapM infer (f : xs)

        let sxs        = substs pile
        let (tf : txs) = types  pile

        let tfi = foldl (flip (:=>)) tresult txs

        su <- unify tf tfi

        let alls = mconcat sxs <> su

        return (alls, apply alls tresult, App f xs)

    infer (Let bindings context) = do
        pile <- forM bindings infer

        let delta = decls pile
        let ss    = mconcat (substs pile)

        (sb, tb, b) <- local (delta <>) $ do
            infer context

        let alls = ss <> sb

        return (alls, apply alls tb, apply alls (Let (results pile) b))

substs =           map $ \(subst, _,  _) -> subst
types  =           map $ \(_,     ty, _) -> ty
decls  = mconcat . map ( \(_,     _,  Binding n _ qty _) -> n =:= qty )
results =          map ( \(_,     _,  x) -> x )

instance Inferrable Binding where
    infer binding@(Binding name args ty body) = do
        tresult          <- fresh
        (func, bindings) <- freshTypesForArgs args tresult

        ty'              <- instantiate ty
        su               <- unify ty' func
        
        (sb, tb, b1) <- 
            ((name =:= ty <> bindings) <>) `local` do
                infer body

        sbu <- unify tb tresult

        let alls = su <> sb <> sbu
        let tyn  = apply alls ty'
        
        ty1 <- generalize tyn

        return (alls, tyn, Binding name args ty1 (apply alls body))
      where
        freshTypesForArgs []       result = return (result, mempty)
        freshTypesForArgs (x : xs) result = do
            (func, bs) <- freshTypesForArgs xs result
            targ       <- fresh
            return (targ :=> func, x =:= Forall mempty targ <> bs)
