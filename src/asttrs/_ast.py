"""
Abstract Syntax Trees: https://docs.python.org/3/library/ast.html
"""
import ast as _ast
import importlib
import sys
from typing import Type

from ._base import AST, immutable

if sys.version_info[0] == 3:
    if 7 <= sys.version_info[1] <= 9:
        name = f"asttrs._py{sys.version_info[0]}_{sys.version_info[1]}"
        module = importlib.import_module(name)

        stmt = getattr(module, "stmt", AST)

        globals().update(module.__dict__)

    else:
        raise ImportError("Support only Python 3.7 to 3.9")


else:
    raise ImportError("Support only Python 3.7 to 3.9")


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
        from asttrs import Expr, Name, Store

        body: str = self.body.strip()

        cmt = body if body.startswith("#") else f"# {body}"

        return Expr(value=Name(id=cmt, ctx=Store())).to_ast()
