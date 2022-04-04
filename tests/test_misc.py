import ast
import json

from asttrs import AST, ClassDef, Comment, FunctionDef
from asttrs._base import Serializable, immutable


def test_serializable():
    @immutable
    class Foo(Serializable):
        x: str

    @immutable
    class Bar(Serializable):
        foo: Foo
        y: int

    @immutable
    class Buz(Serializable):
        x: str
        y: int

    data = dict(foo=dict(x="abc"), y=123)

    assert data == Bar.from_dict(data).to_dict()

    dump = json.dumps(data)

    assert dump == Bar.from_json(dump).to_json()

    data2 = dict(foo=dict(x="abc"), y=456)

    assert data2 == Bar.from_dict(data).evolve(y=456).to_dict()

    assert dict(x="abc") == (
        Foo(x=None).mutate_from_other(Buz.from_dict(dict(x="abc", y=123))).to_dict()
    )


def test_ast():

    assert AST.infer_type_from_ast(ast.ClassDef) == ClassDef
    assert AST.infer_type_from_ast(ast.FunctionDef) == FunctionDef


def test_comment():

    assert Comment.infer_ast_type() == ast.Expr

    assert (
        "# Hello World"
        == Comment.from_ast(Comment(body="Hello World").to_ast()).to_source().strip()
    )

    multilines = "\n".join(["# First line", "# Second line"])

    assert multilines == Comment(body="First line\nSecond line").to_source().strip()
