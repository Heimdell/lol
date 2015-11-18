let add = (x y -> (+ x y)) in

let curry = (f x -> (y -> (f x y))) in

let-rec om-nom-nom! = (_ -> om-nom-nom!) in

let test = (curry add "1") in

(print (test 2) (_ -> halt))
