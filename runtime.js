
// _hole = require("curry")

var _quote = function() {
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

var vararg = function(f) {
    return function() {
        args = []
        for (var i = 0; i < arguments.length; i++) {
            args.push(arguments[i])
        };
        return f(args)
    }
}

var apply = function(f, list) {
    return f.apply(null, list)
}

var init = function(list) {
    return list.slice(0, list.length - 1)
}

var last = function(list) {
    return list[list.length - 1]
}

var _try = function(what, handler) {
    try {
        return what()
    } catch (e) {
        return handler(e.content)
    }
}

var _throw = function(x) {
    throw { content: x }
}

var _dude = function(f, g) {
    return function (x) {
        return f (g (x))
    }
}

var loop = function () {
    var args = []
    for (var i = 0; i < arguments.length - 1; i++) {
        args.push(arguments[i])
    };
    var worker = last(arguments)

    var recur = function() {
        var args = []
        for (var i = 0; i < arguments.length; i++) {
            args.push(arguments[i])
        };
        throw { content: args }
    }

    while (true) {
        args.push(recur)
        try {
            return worker.apply(null, args)
        } catch (e) {
            args = e.content
        }
    }
}