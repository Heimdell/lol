
let uncons = -> list ret ;
    let h = fst list in
    let t = rest list in
    ret h t
in

let x =
    uncons (list 1 2) -> head tail ;
    ++ tail (list head)
in

print x ;
print x ;
halt
