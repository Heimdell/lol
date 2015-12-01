
import Control.Monad.Reader

import Data.List
import Data.Monoid

data AST
    = Var Name
    | Const Const
    | Let [(Name, [Name], Bool, AST)] AST
    | App Name [AST]

data Const
    = String String
    | Number Float

type Name = String

type Context = [(Name, ([Name], Bool))]

data JSCode
    = Chunk [String]
    | Append [JSCode]
    | Tabbed JSCode
    
instance Show JSCode where
    show (Chunk xs) = unwords xs
    show (Append xs) = unwords (map show xs)
    show (Tabbed x)  = show x

toJS :: AST -> Reader Context JSCode
toJS ast = case ast of
    Var name               -> return (Chunk [name])
    Const (String str)     -> return (Chunk [show str])
    Const (Number i)       -> return (Chunk [show i])
    
    Let bindinds context -> do
        let new_part = flip map bindinds $ \(name, args, vararg, _) -> (name, (args, vararg))
        (new_part ++) `local` do
            funs      <- flip mapM bindinds $ \(name, args, _, value) -> do
                jsValue <- toJS (Let [] value)
                return $ Append
                    [ Chunk ["function", name, "(", intercalate ", " args, ") {"]
                    , Tabbed jsValue
                    , Chunk ["}"]
                    ]

            jsContext <- toJS context

            return $ Append (funs ++ [Chunk ["return"], jsContext])

    App f xs' -> do
        Just (args, vararg) <- with lookup f

        let arity   = length args
        let applied = length xs'

        xs <- mapM toJS xs'
        case (arity - applied) `compare` 0 of
            LT | vararg -> do
                let (before, after) = splitAt (arity - 1) xs
                return $ Append $
                    [ Chunk [f, "("]
                    , Append $ intersperse (Chunk [", "]) (before ++ [Chunk []])
                    , Chunk ["["]
                    , Append $ intersperse (Chunk [", "]) after
                    , Chunk ["])"]
                    ]

            LT -> do
                error $ unwords ["too much args for", f]
                    
            EQ | vararg -> do
                let (before, after) = splitAt (arity - 1) xs
                return $ Append $
                    [ Chunk [f, "("]
                    , Append $ intersperse (Chunk [", "]) (before ++ [Chunk []])
                    , Chunk ["["]
                    , Append $ intersperse (Chunk [", "]) after
                    , Chunk ["])"]
                    ]

            EQ -> do
                return $ Append $ 
                    [ Chunk [f, "("]
                    , Append $ intersperse (Chunk [", "]) xs
                    , Chunk [")"]
                    ]

            GT -> do
                let rest = drop applied args
                reduct <- toJS $ App f (xs' ++ map Var rest)
                return $ Append
                    [ Chunk ["function(" ++ intercalate ", " rest ++ ") { return"]
                    , reduct
                    , Chunk ["}"]
                    ]

(|-) :: (Name, ([Name], Bool)) -> Reader Context a -> Reader Context a
x |- action = local (x :) action

with f x = f x <$> ask

test = Let [("list", ["x", "y"], False, (Var "all"))] (
    App "list" 
        [ Const (Number 1)
        , Const (Number 2)
        , Const (Number 3)
        ])