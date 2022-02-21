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


class _AST(Serializable):
    def __repr__(self):
        return str(self)

    def __str__(self):
        return type(self).__name__


@immutable
class AST(_AST):
    @classmethod
    def to_ast_type(cls) -> Type[_ast.AST]:
        return getattr(_ast, cls.__name__)

    @classmethod
    def from_ast_type(cls, _ast_type: Type[_ast.AST]) -> Type["AST"]:
        import asttrs

        return getattr(asttrs, _ast_type.__name__)

    def to_ast(self) -> _ast.AST:
        cls = type(self)

        fields: TUPLE[attr.Attribute, ...] = (
            attr.fields(cls) if attr.has(cls) else tuple()
        )

        ast_type = self.to_ast_type()

        ast_fields: TUPLE[str, ...] = ast_type._fields

        kwargs = {}

        for fd in fields:
            name = fd.name
            if name in ast_fields:

                value = getattr(self, name)

                if isinstance(value, LIST):
                    value = [
                        el.to_ast() if isinstance(el, _AST) else el for el in value
                    ]

                else:
                    value = value.to_ast() if isinstance(value, _AST) else value

                kwargs.update({name: value})

        return ast_type(**kwargs)

    @property
    def ast(self) -> _ast.AST:
        return self.to_ast()

    def to_source(self) -> str:

        return astor.to_source(self.to_ast())

    def dump(self, filepath: str, formatted: bool = False) -> Any:

        code = self.to_source()

        if formatted:
            code = blacking(isorting(code))

        with open(filepath, "w") as f:
            f.write(code)

    @classmethod
    def from_ast(cls, _ast_obj: _ast.AST) -> Optional[Union[LIST["AST"], "AST"]]:

        if isinstance(_ast_obj, (int, str, type(None))):
            return _ast_obj

        elif isinstance(_ast_obj, LIST):
            return [cls.from_ast(el) for el in _ast_obj]

        elif isinstance(_ast_obj, _ast.AST):

            _ast_type: Type[_ast.AST] = type(_ast_obj)

            _cls = cls.from_ast_type(_ast_type)

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
    pass


class Load(expr_context):
    pass


class Store(expr_context):
    pass


class Del(expr_context):
    pass


@immutable
class arg(AST):
    arg: str
    annotation: Optional[str] = None
    type_comment: Optional[str] = None


class expr(AST):
    pass


@immutable
class Name(expr):
    """

    Examples:
    >>> Name(id="xyz").to_source().strip()
    'xyz'
    """

    id: str
    ctx: expr_context = Load()


@immutable
class keyword(AST):
    arg: str
    value: expr


class slice(AST):
    pass


@immutable
class Index(slice):
    value: expr


@immutable
class Call(expr):
    func: expr
    args: LIST[expr] = attr.ib(factory=list)
    keywords: LIST[keyword] = attr.ib(factory=list)


@immutable
class arguments(AST):

    posonlyargs: LIST[arg] = attr.ib(factory=list)
    args: LIST[arg] = attr.ib(factory=list)
    vararg: Optional[arg] = None
    kwonlyargs: LIST[arg] = attr.ib(factory=list)
    kw_defaults: LIST[expr] = attr.ib(factory=list)
    kwarg: Optional[arg] = None
    defaults: LIST[expr] = attr.ib(factory=list)


@immutable
class Constant(expr):
    """

    Exampls:
    >>> Constant(value=123).to_source().strip()
    '(123)'
    """

    value: str
    kind: Optional[str] = None


@immutable
class Subscript(expr):
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
    value: expr


@immutable
class Comment(stmt):

    body: str

    @classmethod
    def to_ast_type(cls) -> Type[_ast.AST]:
        return _ast.Expr

    def to_ast(self) -> _ast.AST:

        body: str = self.body.strip()

        cmt = body if body.startswith("#") else f"# {body}"

        return _ast.Expr(value=_ast.Name(id=cmt))


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
    context_expr: expr
    optional_vars: Optional[expr] = None


@immutable
class With(stmt):
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


class Mult(operator):
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


@immutable
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
class Slice(expr):
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
