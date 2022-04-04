# NOTE: This module is auto-generated according to 'cpython/Parser/Python.asdl',
#       and is combined with the documents from 'cpython/Doc/library/ast.rst'.

from typing import Any
from typing import List as LIST
from typing import Optional

import attr

from asttrs._base import AST, immutable

string = identifier = str
constant = Any
singleton = Optional[bool]


class mod(AST):
    pass


@immutable
class Module(mod):
    body: LIST["stmt"] = attr.ib(factory=list)


@immutable
class Interactive(mod):
    body: LIST["stmt"] = attr.ib(factory=list)


@immutable
class Expression(mod):
    body: "expr"


@immutable
class Suite(mod):
    body: LIST["stmt"] = attr.ib(factory=list)


class stmt(AST):
    pass


@immutable
class FunctionDef(stmt):
    name: "identifier"
    args: "arguments"
    body: LIST["stmt"] = attr.ib(factory=list)
    decorator_list: LIST["expr"] = attr.ib(factory=list)
    returns: "expr" = None


@immutable
class AsyncFunctionDef(stmt):
    name: "identifier"
    args: "arguments"
    body: LIST["stmt"] = attr.ib(factory=list)
    decorator_list: LIST["expr"] = attr.ib(factory=list)
    returns: "expr" = None


@immutable
class ClassDef(stmt):
    name: "identifier"
    bases: LIST["expr"] = attr.ib(factory=list)
    keywords: LIST["keyword"] = attr.ib(factory=list)
    body: LIST["stmt"] = attr.ib(factory=list)
    decorator_list: LIST["expr"] = attr.ib(factory=list)


@immutable
class Return(stmt):
    value: "expr" = None


@immutable
class Delete(stmt):
    targets: LIST["expr"] = attr.ib(factory=list)


@immutable
class Assign(stmt):
    targets: LIST["expr"] = attr.ib(factory=list)
    value: "expr"


@immutable
class AugAssign(stmt):
    target: "expr"
    op: "operator"
    value: "expr"


@immutable
class AnnAssign(stmt):
    target: "expr"
    annotation: "expr"
    value: "expr" = None
    simple: "int"


@immutable
class For(stmt):
    target: "expr"
    iter: "expr"
    body: LIST["stmt"] = attr.ib(factory=list)
    orelse: LIST["stmt"] = attr.ib(factory=list)


@immutable
class AsyncFor(stmt):
    target: "expr"
    iter: "expr"
    body: LIST["stmt"] = attr.ib(factory=list)
    orelse: LIST["stmt"] = attr.ib(factory=list)


@immutable
class While(stmt):
    test: "expr"
    body: LIST["stmt"] = attr.ib(factory=list)
    orelse: LIST["stmt"] = attr.ib(factory=list)


@immutable
class If(stmt):
    test: "expr"
    body: LIST["stmt"] = attr.ib(factory=list)
    orelse: LIST["stmt"] = attr.ib(factory=list)


@immutable
class With(stmt):
    items: LIST["withitem"] = attr.ib(factory=list)
    body: LIST["stmt"] = attr.ib(factory=list)


@immutable
class AsyncWith(stmt):
    items: LIST["withitem"] = attr.ib(factory=list)
    body: LIST["stmt"] = attr.ib(factory=list)


@immutable
class Raise(stmt):
    exc: "expr" = None
    cause: "expr" = None


@immutable
class Try(stmt):
    body: LIST["stmt"] = attr.ib(factory=list)
    handlers: LIST["excepthandler"] = attr.ib(factory=list)
    orelse: LIST["stmt"] = attr.ib(factory=list)
    finalbody: LIST["stmt"] = attr.ib(factory=list)


@immutable
class Assert(stmt):
    test: "expr"
    msg: "expr" = None


@immutable
class Import(stmt):
    names: LIST["alias"] = attr.ib(factory=list)


@immutable
class ImportFrom(stmt):
    module: "identifier" = None
    names: LIST["alias"] = attr.ib(factory=list)
    level: "int" = None


@immutable
class Global(stmt):
    names: LIST["identifier"] = attr.ib(factory=list)


@immutable
class Nonlocal(stmt):
    names: LIST["identifier"] = attr.ib(factory=list)


@immutable
class Expr(stmt):
    value: "expr"


class Pass(stmt):
    pass


class Break(stmt):
    pass


class Continue(stmt):
    pass


class expr(AST):
    pass


@immutable
class BoolOp(expr):
    op: "boolop"
    values: LIST["expr"] = attr.ib(factory=list)


@immutable
class BinOp(expr):
    left: "expr"
    op: "operator"
    right: "expr"


@immutable
class UnaryOp(expr):
    op: "unaryop"
    operand: "expr"


@immutable
class Lambda(expr):
    args: "arguments"
    body: "expr"


@immutable
class IfExp(expr):
    test: "expr"
    body: "expr"
    orelse: "expr"


@immutable
class Dict(expr):
    keys: LIST["expr"] = attr.ib(factory=list)
    values: LIST["expr"] = attr.ib(factory=list)


@immutable
class Set(expr):
    elts: LIST["expr"] = attr.ib(factory=list)


@immutable
class ListComp(expr):
    elt: "expr"
    generators: LIST["comprehension"] = attr.ib(factory=list)


@immutable
class SetComp(expr):
    elt: "expr"
    generators: LIST["comprehension"] = attr.ib(factory=list)


@immutable
class DictComp(expr):
    key: "expr"
    value: "expr"
    generators: LIST["comprehension"] = attr.ib(factory=list)


@immutable
class GeneratorExp(expr):
    elt: "expr"
    generators: LIST["comprehension"] = attr.ib(factory=list)


@immutable
class Await(expr):
    value: "expr"


@immutable
class Yield(expr):
    value: "expr" = None


@immutable
class YieldFrom(expr):
    value: "expr"


@immutable
class Compare(expr):
    left: "expr"
    ops: LIST["cmpop"] = attr.ib(factory=list)
    comparators: LIST["expr"] = attr.ib(factory=list)


@immutable
class Call(expr):
    func: "expr"
    args: LIST["expr"] = attr.ib(factory=list)
    keywords: LIST["keyword"] = attr.ib(factory=list)


@immutable
class Num(expr):
    n: "object"


@immutable
class Str(expr):
    s: "string"


@immutable
class FormattedValue(expr):
    value: "expr"
    conversion: "int" = None
    format_spec: "expr" = None


@immutable
class JoinedStr(expr):
    values: LIST["expr"] = attr.ib(factory=list)


@immutable
class Bytes(expr):
    s: "bytes"


@immutable
class NameConstant(expr):
    value: "singleton"


class Ellipsis(expr):
    pass


@immutable
class Constant(expr):
    value: "constant"


@immutable
class Attribute(expr):
    value: "expr"
    attr: "identifier"
    ctx: "expr_context"


@immutable
class Subscript(expr):
    value: "expr"
    slice: "slice"
    ctx: "expr_context"


@immutable
class Starred(expr):
    value: "expr"
    ctx: "expr_context"


@immutable
class Name(expr):
    id: "identifier"
    ctx: "expr_context"


@immutable
class List(expr):
    elts: LIST["expr"] = attr.ib(factory=list)
    ctx: "expr_context"


@immutable
class Tuple(expr):
    elts: LIST["expr"] = attr.ib(factory=list)
    ctx: "expr_context"


class expr_context(AST):
    pass


class Load(expr_context):
    pass


class Store(expr_context):
    pass


class Del(expr_context):
    pass


class AugLoad(expr_context):
    pass


class AugStore(expr_context):
    pass


class Param(expr_context):
    pass


class slice(AST):
    pass


@immutable
class Slice(slice):
    lower: "expr" = None
    upper: "expr" = None
    step: "expr" = None


@immutable
class ExtSlice(slice):
    dims: LIST["slice"] = attr.ib(factory=list)


@immutable
class Index(slice):
    value: "expr"


class boolop(AST):
    pass


class And(boolop):
    pass


class Or(boolop):
    pass


class operator(AST):
    pass


class Add(operator):
    pass


class Sub(operator):
    pass


class Mult(operator):
    pass


class MatMult(operator):
    pass


class Div(operator):
    pass


class Mod(operator):
    pass


class Pow(operator):
    pass


class LShift(operator):
    pass


class RShift(operator):
    pass


class BitOr(operator):
    pass


class BitXor(operator):
    pass


class BitAnd(operator):
    pass


class FloorDiv(operator):
    pass


class unaryop(AST):
    pass


class Invert(unaryop):
    pass


class Not(unaryop):
    pass


class UAdd(unaryop):
    pass


class USub(unaryop):
    pass


class cmpop(AST):
    pass


class Eq(cmpop):
    pass


class NotEq(cmpop):
    pass


class Lt(cmpop):
    pass


class LtE(cmpop):
    pass


class Gt(cmpop):
    pass


class GtE(cmpop):
    pass


class Is(cmpop):
    pass


class IsNot(cmpop):
    pass


class In(cmpop):
    pass


class NotIn(cmpop):
    pass


@immutable
class comprehension(AST):
    target: "expr"
    iter: "expr"
    ifs: LIST["expr"] = attr.ib(factory=list)
    is_async: "int"


class excepthandler(AST):
    pass


@immutable
class ExceptHandler(excepthandler):
    type: "expr" = None
    name: "identifier" = None
    body: LIST["stmt"] = attr.ib(factory=list)


@immutable
class arguments(AST):
    args: LIST["arg"] = attr.ib(factory=list)
    vararg: "arg" = None
    kwonlyargs: LIST["arg"] = attr.ib(factory=list)
    kw_defaults: LIST["expr"] = attr.ib(factory=list)
    kwarg: "arg" = None
    defaults: LIST["expr"] = attr.ib(factory=list)


@immutable
class arg(AST):
    arg: "identifier"
    annotation: "expr" = None


@immutable
class keyword(AST):
    arg: "identifier" = None
    value: "expr"


@immutable
class alias(AST):
    name: "identifier"
    asname: "identifier" = None


@immutable
class withitem(AST):
    context_expr: "expr"
    optional_vars: "expr" = None
