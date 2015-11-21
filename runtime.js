
var list = function() {
    var res = []
    for (var i = 0; i < arguments.length; i++) {
        res.push(arguments[i])
    }
    return res
}

var fst = function(arr) {
    return arr[0]
}

var rest = function(arr) {
    return arr.slice(1)
}

var _plus_plus = function(x, y) {
    return x.concat(y)
}

var print = function (x, ret) {
    console.log(x)
    return ret()
}

var halt = function() {
    return null
}