import ast as _ast
import json
import re
from typing import Any
from typing import Dict as DICT
from typing import List as LIST
from typing import Optional
from typing import Tuple as TUPLE
from typing import Type, Union

import astor
import attr
import cattr

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
        print(self.to_source().strip())

    @classmethod
    def from_file(cls, filepath: str) -> "AST":

        with open(filepath, "r") as f:
            source = f.read()

        return cls.from_source(source)

    def to_file(self, filepath: str, formatted: bool = False) -> Any:
        from asttrs.utils import blacking, isorting

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
class Example(Serializable):
    source: str
    want: str


@immutable
class Defination(Serializable):
    name: str
    docstring: Optional[str] = None
    examples: LIST[Example] = attr.ib(factory=list)

    @classmethod
    def iter_from_doc(cls, doc: str):
        ANCHOR_CLASS = ".. class::"
        ANCHOR_SECTION = "\n\n.."
        ANCHOR_DOUBLE_NEWLINE = "\n\n"
        ANCHOR_DOCTEST = ".. doctest::"

        while doc.strip():
            s = doc.find(ANCHOR_CLASS)
            if s < 0:
                break

            e = doc[s:].find(ANCHOR_DOUBLE_NEWLINE)
            if e < 0:
                break

            dfns = doc[s : s + e]  # NOQA: E203
            residual = doc[s + e :]  # NOQA: E203

            idx = [
                v
                for v in (residual.find(ANCHOR_SECTION), residual.find(ANCHOR_DOCTEST))
                if v >= 0
            ]
            if not idx:
                break

            t = min(idx)
            docstring = cls._clean_doc(residual[:t])

            for name in cls._parse_names(dfns):
                yield cls(name=name, docstring=docstring)

            doc = residual[t:]

    @staticmethod
    def _parse_names(doc: str) -> LIST[str]:
        return re.findall(r"(\w+)\(", doc)

    @staticmethod
    def _clean_doc(doc: str) -> str:
        return re.sub(r"\n+\s+", "\n", doc).strip()
