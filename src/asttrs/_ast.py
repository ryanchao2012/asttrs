"""
Abstract Syntax Trees: https://docs.python.org/3/library/ast.html
"""

import ast as _ast
import json
from typing import Any
from typing import Dict as DICT
from typing import List as LIST
from typing import Optional
from typing import Tuple as TUPLE
from typing import Type, Union

import astor
import attr
import cattr

from asttrs.utils import blacking, isorting

immutable = attr.s(auto_attribs=True, slots=True, frozen=True, kw_only=True)


@immutable
class Serializable:
    def to_dict(self, recurse=True, **kwargs):
        return attr.asdict(self, recurse=recurse, **kwargs)

    @classmethod
    def from_dict(cls, data: DICT):
        return cattr.structure_attrs_fromdict(data, cls)

    @classmethod
    def from_json(cls, json_str: str):
        return cls.from_dict(json.loads(json_str))

    def to_json(self, ensure_ascii=False, **kwargs):
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, **kwargs)

    def evolve(self, **kwargs):
        return attr.evolve(self, **kwargs)

    def mutate_from_other(self, other: "Serializable", excludes=[]):
        self_fields = [f2.name for f2 in attr.fields(self.__class__)]

        valid_fields = [
            f1.name
            for f1 in attr.fields(other.__class__)
            if (getattr(other, f1.name, None) is not None)
            and (f1.name not in excludes)
            and (f1.name in self_fields)
        ]

        data = other.to_dict(filter=lambda att, value: att.name in valid_fields)

        return self.evolve(**data)


@immutable
class AST(Serializable):
    @classmethod
    def infer_ast_type(cls) -> Type[_ast.AST]:
        return getattr(_ast, cls.__name__)

    @classmethod
    def infer_type_from_ast(cls, _ast_type: Type[_ast.AST]) -> Type["AST"]:
        import asttrs

        return getattr(asttrs, _ast_type.__name__)

    def to_ast(self) -> _ast.AST:
        cls = type(self)

        fields: TUPLE[attr.Attribute, ...] = (
            attr.fields(cls) if attr.has(cls) else tuple()
        )

        ast_type = self.infer_ast_type()

        ast_fields: TUPLE[str, ...] = ast_type._fields

        kwargs = {}

        for fd in fields:
            name = fd.name
            if name in ast_fields:

                value = getattr(self, name)

                if isinstance(value, LIST):
                    value = [el.to_ast() if isinstance(el, AST) else el for el in value]

                else:
                    value = value.to_ast() if isinstance(value, AST) else value

                kwargs.update({name: value})

        return ast_type(**kwargs)

    @classmethod
    def from_source(cls, source: str) -> "AST":

        return cls.from_ast(_ast.parse(source))

    def to_source(self) -> str:

        return astor.to_source(self.to_ast())

    def show(self) -> None:
        print(self.to_source())

    @classmethod
    def from_file(cls, filepath: str) -> "AST":

        with open(filepath, "r") as f:
            source = f.read()

        return cls.from_source(source)

    def to_file(self, filepath: str, formatted: bool = False) -> Any:

        code = self.to_source()

        if formatted:
            code = blacking(isorting(code))

        with open(filepath, "w") as f:
            f.write(code)

    @classmethod
    def from_ast(cls, _ast_obj: _ast.AST) -> Optional[Union[LIST["AST"], "AST"]]:

        if isinstance(
            _ast_obj, (int, str, bytes, float, complex, type(Ellipsis), type(None))
        ):
            return _ast_obj

        elif isinstance(_ast_obj, LIST):
            return [cls.from_ast(el) for el in _ast_obj]

        elif isinstance(_ast_obj, _ast.AST):

            _ast_type: Type[_ast.AST] = type(_ast_obj)

            _cls = cls.infer_type_from_ast(_ast_type)

            return _cls(
                **{
                    f.name: cls.from_ast(getattr(_ast_obj, f.name, None))
                    for f in attr.fields(_cls)
                }
            )

        else:
            raise TypeError(_ast_obj)


@immutable
class TypeIgnore(AST):
    lineno: int
    tag: str


@immutable
class alias(AST):
    """Both parameters are raw strings of the names. asname can be None if the regular name is to be used."""

    name: str
    asname: Optional[str] = None


class expr_context(AST):
    """Variable references can be used to load the value of a variable, to assign a new value to it, or to delete it.
    Variable references are given a context to distinguish these cases.
    """

    pass


class Load(expr_context):
    pass


class Store(expr_context):
    pass


class Del(expr_context):
    pass


@immutable
class arg(AST):
    """A single argument in a list.

    Args:
        arg: is a raw string of the argument name.

        annotation: is its annotation, such as a Str or Name node.

        type_comment: is an optional string with the type annotation as a comment
    """

    arg: str
    annotation: Optional[str] = None
    type_comment: Optional[str] = None


class expr(AST):
    pass


class boolop(AST):
    "Boolean operator tokens."
    pass


class And(boolop):
    pass


class Or(boolop):
    pass


@immutable
class Name(expr):
    """A variable name.

    Args:
        id: holds the name as a string.

        ctx: is one of the following types.

    Examples:
    >>> Name(id="xyz").to_source().strip()
    'xyz'
    """

    id: str
    ctx: expr_context = Load()


@immutable
class keyword(AST):
    """A keyword argument to a function call or class definition.

    Args:
        arg: is a raw string of the parameter name.

        value: is a node to pass in.
    """

    arg: str
    value: expr


class slice(AST):
    pass


@immutable
class Index(slice):
    value: expr


@immutable
class Call(expr):
    """A function call.

    Args:
        func: is the function, which will often be a Name or Attribute object.

        args: holds a list of the arguments passed by position.

        keywords: holds a list of keyword objects representing arguments passed by keyword.

    When creating a Call node, args and keywords are required, but they can be empty lists. starargs and kwargs are optional.

    """

    func: expr
    args: LIST[expr] = attr.ib(factory=list)
    keywords: LIST[keyword] = attr.ib(factory=list)


@immutable
class arguments(AST):
    """The arguments for a function.

    Args:
        posonlyargs, args and kwonlyargs: are lists of arg nodes.

        vararg and kwarg: are single arg nodes, referring to the *args, **kwargs parameters.

        kw_defaults: is a list of default values for keyword-only arguments. If one is None, the corresponding argument is required.

        defaults: is a list of default values for arguments that can be passed positionally.
        If there are fewer defaults, they correspond to the last n arguments.
    """

    posonlyargs: LIST[arg] = attr.ib(factory=list)
    args: LIST[arg] = attr.ib(factory=list)
    vararg: Optional[arg] = None
    kwonlyargs: LIST[arg] = attr.ib(factory=list)
    kw_defaults: LIST[expr] = attr.ib(factory=list)
    kwarg: Optional[arg] = None
    defaults: LIST[expr] = attr.ib(factory=list)


@immutable
class Constant(expr):
    """A constant value.

    Args:
        value: contains the Python object it represents.
        The values represented can be simple types such as a number, string or None, but also immutable container types (tuples and frozensets)
        if all of their elements are constant.

    Exampls:
    >>> Constant(value=123).to_source().strip()
    '(123)'
    """

    value: str
    kind: Optional[str] = None


@immutable
class Subscript(expr):
    """A subscript, such as l[1].

    Args:
        value: is the subscripted object (usually sequence or mapping).

        slice: is an index, slice or key. It can be a Tuple and contain a Slice.

        ctx: is Load, Store or Del according to the action performed with the subscript.

    """

    value: expr
    slice: expr
    ctx: expr_context = Load()


class stmt(AST):
    pass


@immutable
class Delete(stmt):
    """Represents a del statement.

    Args:
        targets is a list of nodes, such as Name, Attribute or Subscript nodes.

    Examples:
    >>> Delete(targets=[Name(id='x'), Name(id='y'), Name(id='z')]).to_source().strip()
    'del x, y, z'
    """

    targets: LIST[expr]


@immutable
class Assert(stmt):
    """An assertion.

    Args:
        test: holds the condition, such as a Compare node.
        msg: holds the failure message.

    Examples:
    >>> Assert(test=Name(id='x'), msg=Name(id='y')).to_source().strip()
    'assert x, y'
    """

    test: expr
    msg: Optional[expr] = None


@immutable
class Expr(stmt):
    """When an expression, such as a function call, appears as a statement by itself with its return value not used or stored, it is wrapped in this container.

    Args:
        value: holds one of the other nodes in this section, a Constant, a Name, a Lambda, a Yield or YieldFrom node.

    >>> Expr(value=UnaryOp(op=USub(), operand=Name(id='a'))).to_source().strip()
    '-a'
    """

    value: expr


@immutable
class Comment(stmt):
    """A Comment wrapper for convenient purpose, since there's no comment node in ast.

    Args:
        body: comment string

    >>> Comment(body="This is a comment").to_source().strip()
    '# This is a comment'
    """

    body: str

    @classmethod
    def infer_ast_type(cls) -> Type[_ast.AST]:
        return _ast.Expr

    def to_ast(self) -> _ast.AST:

        body: str = self.body.strip()

        cmt = body if body.startswith("#") else f"# {body}"

        return Expr(value=Name(id=cmt)).to_ast()


@immutable
class Assign(stmt):
    """An assignment.
    Args:
        targets: is a list of nodes.
        value: is a single node.

    Multiple nodes in targets represents assigning the same value to each.
    Unpacking is represented by putting a Tuple or List within targets.

    Examples:
    >>> Assign(targets=[Name(id='a'), Name(id='b')],
    ...        value=Constant(value=1)).to_source().strip()
    'a = b = 1'

    >>> Assign(
    ...     targets=[Tuple(elts=[Name(id='a'), Name(id='b')])],
    ...     value=Name(id='c')
    ... ).to_source().strip()
    'a, b = c'
    """

    targets: LIST[expr]
    value: expr
    type_comment: Optional[str] = None


class Pass(stmt):
    """A pass statement.

    Examples:
    >>> Pass().to_source().strip()
    'pass'
    """

    pass


class Break(stmt):
    pass


class Continue(stmt):
    pass


@immutable
class FunctionDef(stmt):
    """A function definition.

    Args:
        name: is a raw string of the function name.

        args: is an arguments node.

        body: is the list of nodes inside the function.

        decorator_list: is the list of decorators to be applied, stored outermost first (i.e. the first in the list will be applied last).

        returns: is the return annotation.
    """

    name: str
    args: arguments = attr.ib(default=arguments())
    body: LIST[stmt] = attr.ib(default=[Pass()])
    decorator_list: LIST[expr] = attr.ib(factory=list)
    returns: Optional[expr] = None
    type_comment: Optional[str] = None


@immutable
class withitem(AST):
    """A single context manager in a with block.

    Args:
        context_expr: is the context manager, often a Call node.
        optional_vars: is a Name, Tuple or List for the as foo part, or None if that isn't used.

    """

    context_expr: expr
    optional_vars: Optional[expr] = None


@immutable
class With(stmt):
    """A with block.

    Args:
        items: is a list of withitem nodes representing the context managers, and body is the indented block inside the context.

    """

    items: LIST[withitem]
    body: LIST[stmt] = attr.ib(default=[Pass()])
    type_comment: Optional[str] = None


@immutable
class Module(AST):
    body: LIST[stmt] = attr.ib(factory=list)
    type_ignores: LIST[TypeIgnore] = attr.ib(factory=list)


@immutable
class ClassDef(stmt):
    """A class definition.

    Args:
        name: is a raw string for the class name

        bases: is a list of nodes for explicitly specified base classes.

        keywords: is a list of keyword nodes, principally for 'metaclass'. Other keywords will be passed to the metaclass, as per PEP-3115.

        starargs, kwargs: are each a single node, as in a function call.
        starargs will be expanded to join the list of base classes, and kwargs will be passed to the metaclass.

        body: is a list of nodes representing the code within the class definition.

        decorator_list: is a list of nodes, as in FunctionDef.
    """

    name: str
    bases: LIST[expr] = attr.ib(factory=list)
    keywords: LIST[keyword] = attr.ib(factory=list)
    body: LIST[stmt] = attr.ib(default=[Pass()])
    decorator_list: LIST[expr] = attr.ib(factory=list)


@immutable
class AnnAssign(stmt):
    """An assignment with a type annotation.

    Args:
        target: is a single node and can be a Name, a Attribute or a Subscript.
        annotation: is the annotation, such as a Constant or Name node.
        value: is a single optional node.
        simple: is a boolean integer set to True for a Name node in target
        that do not appear in between parenthesis and are hence pure names and not expressions.

    """

    target: expr
    annotation: expr
    value: Optional[expr] = None
    simple: int = 1


@immutable
class Import(stmt):
    """An import statement.
    Args:
        names is a list of alias nodes.

    Examples:
    >>> Import(
    ...     names=[alias(name='x'), alias(name='y'), alias(name='z')]
    ... ).to_source().strip()
    'import x, y, z'
    """

    names: LIST[alias] = attr.ib(factory=list)


@immutable
class ImportFrom(stmt):
    """Represents from x import y.
        Args:
            module: is a raw string of the 'from' name, without any leading dots, or None for statements such as from . import foo.
            level: is an integer holding the level of the relative import (0 means absolute import).

        Examples:
        >>> ImportFrom(
        ...     module='y',
        ...     names=[alias(name='x'), alias(name='y'), alias(name='z')]
        ... ).to_source().strip()
        'from y import x, y, z'

    >>>

    """

    module: str
    names: LIST[alias] = attr.ib(factory=list)
    level: int = 0


class operator(AST):
    """Binary operator tokens."""

    pass


class RShift(operator):
    pass


class LShift(operator):
    pass


class Mult(operator):
    pass


class Div(operator):
    pass


class FloorDiv(operator):
    pass


class Mod(operator):
    pass


class Pow(operator):
    pass


class MatMult(operator):
    pass


class BitOr(operator):
    pass


class BitXor(operator):
    pass


class BitAnd(operator):
    pass


class Add(operator):
    pass


class Sub(operator):
    pass


@immutable
class Lambda(expr):
    """lambda is a minimal function definition that can be used inside an expression. Unlike FunctionDef, body holds a single node."""

    args: arguments
    body: expr


@immutable
class BinOp(expr):
    """A binary operation (like addition or division).

    Args:
        op is the operator.
        left, right: are any expression nodes.

    Examples:
    >>> BinOp(left=Name(id='x'), op=Add(), right=Name(id='y')).to_source().strip()
    '(x + y)'

    >>> BinOp(left=Name(id='x'), op=Sub(), right=Name(id='y')).to_source().strip()
    '(x - y)'

    >>> BinOp(left=Name(id='x'), op=Mult(), right=Name(id='y')).to_source().strip()
    '(x * y)'

    >>> BinOp(left=Name(id='x'), op=RShift(), right=Name(id='y')).to_source().strip()
    '(x >> y)'

    """

    left: expr
    op: operator
    right: expr


@immutable
class Return(stmt):
    """A return statement.

    Examples:
    >>> Return(value=Constant(value=4)).to_source().strip()
    'return 4'
    """

    value: Optional[expr] = None


class unaryop(AST):
    """Unary operator tokens. Not is the not keyword, Invert is the ~ operator."""

    pass


class Invert(unaryop):
    pass


class Not(unaryop):
    pass


class UAdd(unaryop):
    pass


class USub(unaryop):
    pass


@immutable
class UnaryOp(expr):
    """A unary operation.
    Args:
        op: is the operator.
        operand: any expression node.

    Examples:
    >>> UnaryOp(op=Not(), operand=Name(id='x')).to_source().strip()
    '(not x)'

    >>> UnaryOp(op=USub(), operand=Name(id='x')).to_source().strip()
    '(-x)'

    >>> UnaryOp(op=UAdd(), operand=Name(id='x')).to_source().strip()
    '(+x)'

    >>> UnaryOp(op=Invert(), operand=Name(id='x')).to_source().strip()
    '(~x)'

    """

    op: unaryop
    operand: expr


@immutable
class List(expr):
    """A list or tuple.

    Args:
        elts: holds a list of nodes representing the elements.
        ctx: is Store if the container is an assignment target (i.e. (x,y)=something), and Load otherwise.

    Exampls:
    >>> List(elts=[Constant(value=1), Constant(value=2), Constant(value=3)]).to_source().strip()
    '[1, 2, 3]'

    >>> Tuple(elts=[Constant(value='a'), Constant(value='b'), Constant(value='c')]).to_source().strip()
    "('a', 'b', 'c')"
    """

    elts: LIST[expr] = attr.ib(factory=list)
    ctx: expr_context = Load()


class Tuple(List):
    pass


@immutable
class Set(expr):
    """A set.

    Args:
        elts: holds a list of nodes representing the set's elements.

    Examples:
    >>> Set(elts=[Constant(value='a'), Constant(value='b'), Constant(value='c')]).to_source().strip()
    "{'a', 'b', 'c'}"
    """

    elts: LIST[expr] = attr.ib(factory=list)


@immutable
class Dict(expr):
    """A dictionary.

    Args:
        keys, values: hold lists of nodes representing the keys and the values respectively,
        in matching order (what would be returned when calling dictionary.keys() and dictionary.values()).

        When doing dictionary unpacking using dictionary literals the expression to be expanded goes in the values list,
        with a None at the corresponding position in keys.

    Examples:
    >>> Dict(keys=[Constant(value='a'), None], values=[Constant(value=1), Name(id='d')]).to_source().strip()
    "{'a': 1, **d}"
    """

    keys: LIST[Optional[expr]]
    values: LIST[expr]


@immutable
class Attribute(expr):
    """Attribute access, e.g. d.keys.

    Args:
        value: is a node, typically a Name.
        attr: is a bare string giving the name of the attribute.
        ctx: is Load, Store or Del according to how the attribute is acted on.

    Examples:
    >>> Attribute(value=Name(id='snake'), attr='colour').to_source().strip()
    'snake.colour'
    """

    value: expr
    attr: str
    ctx: expr_context = Load()


@immutable
class Slice(slice):
    """Regular slicing (on the form lower:upper or lower:upper:step). Can occur only inside the slice field of Subscript, either directly or as an element of Tuple.

    Examples:
    >>> Subscript(
    ...     value=Name(id='l'),
    ...     slice=Slice(lower=Constant(value=1), upper=Constant(value=2))
    ... ).to_source().strip()
    'l[1:2]'
    """

    lower: Optional[expr] = None
    upper: Optional[expr] = None
    step: Optional[expr] = None


@immutable
class ExtSlice(slice):
    dims: LIST[slice]


@immutable
class JoinedStr(expr):
    """An f-string, comprising a series of FormattedValue and Constant nodes."""

    values: LIST[expr] = attr.ib(factory=list)


@immutable
class FormattedValue(expr):
    """Node representing a single formatting field in an f-string.
    If the string contains a single formatting field and nothing else the node can be isolated otherwise it appears in JoinedStr.

    Args:
        value: is any expression node (such as a literal, a variable, or a function call).
        conversion: is an integer:
            -1: no formatting
            115: !s string formatting
            114: !r repr formatting
            97: !a ascii formatting
        format_spec: is a JoinedStr node representing the formatting of the value, or None if no format was specified.
        Both conversion and format_spec can be set at the same time.

    """

    value: expr
    conversion: Optional[int] = None
    format_spec: Optional[expr] = None


@immutable
class Starred(expr):
    """A *var variable reference.

    Args:
        value: holds the variable, typically a Name node. This type must be used when building a Call node with *args.

    Examples:
    >>> Assign(
    ...     targets=[Tuple(elts=[Name(id='a'),
    ...              Starred(value=Name(id='b'))])],
    ...     value=Name(id='it')
    ... ).to_source().strip()
    'a, *b = it'
    """

    value: expr
    ctx: expr_context = Load()


@immutable
class IfExp(expr):
    """An expression such as a if b else c. Each field holds a single node, so in the following example, all three are Name nodes.

    Examples:

    >>> IfExp(
    ...     test=Name(id='b'),
    ...     body=Name(id='a'),
    ...     orelse=Name(id='c')
    ... ).to_source().strip()
    '(a if b else c)'
    """

    test: expr
    body: expr
    orelse: expr


@immutable
class If(stmt):
    """An if statement.

    Args:
        test: holds a single node, such as a Compare node. body and orelse: each hold a list of nodes.

    """

    test: expr
    body: LIST[stmt]
    orelse: LIST[stmt] = attr.ib(factory=list)


@immutable
class For(stmt):
    """A for loop.

    Args:
        target: holds the variable(s) the loop assigns to, as a single Name, Tuple or List node.

        iter: holds the item to be looped over, again as a single node.

        body and orelse: contain lists of nodes to execute. Those in orelse are executed if the loop finishes normally, rather than via a break statement.

    """

    target: expr
    iter: expr
    body: LIST[stmt]
    orelse: LIST[stmt] = attr.ib(factory=list)
    type_comment: Optional[str] = None


@immutable
class BoolOp(expr):
    """A boolean operation, 'or' or 'and'.

    Args:
        op: is Or or And.

        values: are the values involved. Consecutive operations with the same operator, such as a or b or c, are collapsed into one node with several values.

    Examples:
    >>> BoolOp(
    ...     op=Or(),
    ...     values=[Name(id='x'), Name(id='y')]
    ... ).to_source().strip()
    '(x or y)'
    """

    op: boolop
    values: LIST[expr]


class excepthandler(AST):
    pass


@immutable
class ExceptHandler(excepthandler):
    """A single except clause.

    Args:
        type: is the exception type it will match, typically a Name node (or None for a catch-all except: clause).

        name: is a raw string for the name to hold the exception, or None if the clause doesn't have as foo.

        body: is a list of nodes.

    """

    type: Optional[expr]
    name: str
    body: LIST[stmt]


@immutable
class Try(stmt):
    """try blocks. All attributes are list of nodes to execute, except for handlers, which is a list of ExceptHandler nodes."""

    body: LIST[stmt]
    handlers: LIST[excepthandler]
    orelse: LIST[stmt] = attr.ib(factory=list)
    finalbody: LIST[stmt] = attr.ib(factory=list)


class cmpop(AST):
    """Comparison operator tokens."""

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
class Compare(expr):
    """A comparison of two or more values.

    Args:
        left: is the first value in the comparison,

        ops: the list of operators.

        comparators: the list of values after the first element in the comparison.

    Examples:
    >>> Compare(
    ...     left=Constant(value=1),
    ...     ops=[LtE(), Lt()],
    ...     comparators=[Name(id='a'), Constant(value=10)]
    ... ).to_source().strip()
    '(1 <= a < 10)'
    """

    left: expr
    ops: LIST[cmpop] = attr.ib(factory=list)
    comparators: LIST[expr] = attr.ib(factory=list)


@immutable
class comprehension(AST):
    target: expr
    iter: expr
    ifs: LIST[expr]
    is_async: int


@immutable
class ListComp(expr):
    """List and set comprehensions, generator expressions, and dictionary comprehensions.

    Args:
        elt (or key and value): is a single node representing the part that will be evaluated for each item.

        generators: is a list of comprehension nodes.

    """

    elt: expr
    generators: LIST[comprehension]


class SetComp(ListComp):
    pass


class GeneratorExp(ListComp):
    pass


@immutable
class DictComp(expr):
    key: expr
    value: expr
    generators: LIST[comprehension]


@immutable
class Yield(expr):
    """A yield or yield from expression. Because these are expressions, they must be wrapped in a Expr node if the value sent back is not used.

    Examples:
    >>> Yield(value=Name(id='x')).to_source().strip()
    '(yield x)'

    >>> YieldFrom(value=Name(id='x')).to_source().strip()
    '(yield from x)'
    """

    value: Optional[expr] = None


class YieldFrom(Yield):
    pass


@immutable
class Raise(stmt):
    """A raise statement.

    Args:
        exc: is the exception object to be raised, normally a Call or Name, or None for a standalone raise.

        cause: is the optional part for y in raise x from y.

    Examples:
    >>> Raise().to_source().strip()
    'raise'

    >>> Raise(exc=Name(id='x'), cause=Name(id='y')).to_source().strip()
    'raise x from y'
    """

    exc: Optional[expr] = None
    cause: Optional[expr] = None


class AsyncFunctionDef(FunctionDef):
    """An async def function definition. Has the same fields as FunctionDef."""

    pass


@immutable
class Await(expr):
    """An await expression. value is what it waits for. Only valid in the body of an AsyncFunctionDef."""

    value: expr


@immutable
class AugAssign(stmt):
    """Augmented assignment, such as a += 1.

    Args:
        target: is a Name node for x (with the Store context).

        op: is binary operator.

        value: is expression.

    Examples:
    >>> AugAssign(
    ...     target=Name(id='x'),
    ...     op=Add(),
    ...     value=Constant(value=2)
    ... ).to_source().strip()
    'x += 2'
    """

    target: expr
    op: operator
    value: expr


@immutable
class Global(stmt):
    """global and nonlocal statements.

    Args:
        names: is a list of raw strings.

    Examples:
    >>> Global(names=['x', 'y', 'z']).to_source().strip()
    'global x, y, z'

    >>> Nonlocal(names=['x', 'y', 'z']).to_source().strip()
    'nonlocal x, y, z'
    """

    names: LIST[str]


class Nonlocal(Global):
    pass


@immutable
class While(stmt):
    """A while loop.

    Args:
        test: holds the condition, such as a Compare node.

    """

    test: expr
    body: LIST[stmt]
    orelse: LIST[stmt] = attr.ib(factory=list)
    pass


class AsyncWith(With):
    """async for loops and async with context managers. They have the same fields as For and With, respectively.
    Only valid in the body of an AsyncFunctionDef"""

    pass


class AsyncFor(For):
    """async for loops and async with context managers. They have the same fields as For and With, respectively.
    Only valid in the body of an AsyncFunctionDef"""

    pass
