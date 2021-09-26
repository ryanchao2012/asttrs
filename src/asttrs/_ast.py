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
        valid_fields = [
            f1.name
            for f1 in attr.fields(other.__class__)
            if (getattr(other, f1.name, None) is not None)
            and (f1.name not in excludes)
            and (f1.name in [f2.name for f2 in attr.fields(self.__class__)])
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
    def get_ast_type(cls) -> Type[_ast.AST]:
        return getattr(_ast, cls.__name__)

    @classmethod
    def map_asttrs_type(cls, _ast_type: Type[_ast.AST]) -> Type["AST"]:
        import asttrs

        return getattr(asttrs, _ast_type.__name__)

    @property
    def ast(self) -> _ast.AST:
        cls = type(self)
        fields: TUPLE[attr.Attribute, ...] = (
            attr.fields(cls) if attr.has(cls) else tuple()
        )

        ast_type = self.get_ast_type()

        ast_fields: TUPLE[str, ...] = ast_type._fields

        kwargs = {}

        for fd in fields:
            _name = fd.name
            if _name in ast_fields:

                value = getattr(self, _name)

                if isinstance(value, LIST):
                    value = [v.ast if isinstance(v, _AST) else v for v in value]

                else:
                    value = value.ast if isinstance(value, _AST) else value

                kwargs.update({_name: value})

        return ast_type(**kwargs)

    def render(self) -> str:

        return astor.to_source(self.ast)

    def dump(self, filepath: str, formatted: bool = False) -> Any:

        code = self.render()

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

            _cls = cls.map_asttrs_type(_ast_type)

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
class Expr(stmt):
    value: expr


@immutable
class Comment(stmt):

    body: str

    @classmethod
    def get_ast_type(cls) -> Type[_ast.AST]:
        return _ast.Expr

    @property
    def ast(self) -> _ast.AST:

        body: str = self.body.strip()

        cmt = body if body.startswith("#") else f"# {body}"

        return _ast.Expr(value=_ast.Name(id=cmt))


@immutable
class Assign(stmt):
    targets: LIST[expr]
    value: expr
    type_comment: Optional[str] = None


class Pass(stmt):
    pass


@immutable
class FunctionDef(stmt):
    name: str
    args: arguments
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
    name: str
    bases: LIST[expr] = attr.ib(factory=list)
    keywords: LIST[keyword] = attr.ib(factory=list)
    body: LIST[stmt] = attr.ib(default=[Pass()])
    decorator_list: LIST[expr] = attr.ib(factory=list)


@immutable
class AnnAssign(stmt):
    target: expr
    annotation: expr
    value: Optional[expr] = None
    simple: int = 1


@immutable
class Code(Serializable):

    modname: str
    module: Module = Module(body=[])


@immutable
class Import(stmt):
    names: LIST[alias] = attr.ib(factory=list)


@immutable
class ImportFrom(stmt):
    module: str
    names: LIST[alias] = attr.ib(factory=list)
    level: int = 0


class operator(AST):
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
    args: arguments
    body: expr


@immutable
class BinOp(expr):
    left: expr
    op: operator
    right: expr


@immutable
class Return(stmt):
    value: Optional[expr] = None


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


@immutable
class UnaryOp(expr):
    op: unaryop
    operand: expr


@immutable
class List(expr):
    elts: LIST[expr] = attr.ib(factory=list)
    ctx: expr_context = Load()


@immutable
class Tuple(expr):
    elts: LIST[expr] = attr.ib(factory=list)
    ctx: expr_context = Load()


@immutable
class Attribute(expr):
    value: expr
    attr: str
    ctx: expr_context = Load()


@immutable
class Slice(expr):
    lower: Optional[expr] = None
    upper: Optional[expr] = None
    step: Optional[expr] = None


@immutable
class JoinedStr(expr):
    values: LIST[expr] = attr.ib(factory=list)


@immutable
class FormattedValue(expr):
    value: expr
    conversion: Optional[int] = None
    format_spec: Optional[expr] = None


@immutable
class Starred(expr):
    value: expr
    ctx: expr_context = Load()
