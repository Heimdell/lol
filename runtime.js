
// _hole = require("curry")

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

var s = JSON.stringify
var l = console.log

var _plus_plus = function(x, y) {
    // l("++ " + s(x) + " " + s(y))
    return x.concat(y)
}

var _plus = function(x, y) {
    return x + y
}

var print = function (x, ret) {
    console.log(x)
    return ret()
}

var halt = function() {
    return null
}

var _wat = function(flag, yes_cont, no_cont) {
    if (flag) {
        return yes_cont()
    } else {
        return no_cont()
    }
}

var null_wat = function(list) {
    return list.length == 0
}

function rec(f) {
    return f(function () {
        args = []
        for (var i = 0; i < arguments.length; i++) {
            args.push(arguments[i])
        };
        return rec(f).apply(null, args) 
    })
}

