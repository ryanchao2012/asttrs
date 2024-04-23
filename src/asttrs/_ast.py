"""
Abstract Syntax Trees: https://docs.python.org/3/library/ast.html
"""

import ast as _ast
import sys
import warnings
from typing import Type

from ._base import AST, immutable

if (3, 7) <= sys.version_info < (3, 8):
    import asttrs._py3_7 as _asttrs
    from asttrs._py3_7 import *  # noqa

    pass


elif (3, 8) <= sys.version_info < (3, 9):
    import asttrs._py3_8 as _asttrs
    from asttrs._py3_8 import *  # noqa

    pass

elif (3, 9) <= sys.version_info < (3, 10):
    import asttrs._py3_9 as _asttrs
    from asttrs._py3_9 import *  # noqa

    pass

elif (3, 10) <= sys.version_info < (3, 11):
    import asttrs._py3_10 as _asttrs
    from asttrs._py3_10 import *  # noqa

    pass

elif (3, 11) <= sys.version_info < (3, 12):
    import asttrs._py3_11 as _asttrs
    from asttrs._py3_11 import *  # noqa

    pass

else:
    import asttrs._py3_12 as _asttrs
    from asttrs._py3_12 import *  # noqa

    pass


if (3, 11) <= sys.version_info:
    warnings.warn(
        "For Python 3.11 and later, a few ast types may not be supported, such as FunctionType, ParamSpec, TypeAlias, TypeVar, and etc.",
        UserWarning,
    )


stmt = getattr(_asttrs, "stmt", AST)


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

        lines = [body.strip() for body in self.body.split("\n") if body.strip()]

        cmt: str = "\n".join(
            [body if body.startswith("#") else f"# {body}" for body in lines]
        )

        return Expr(value=Name(id=cmt, ctx=Store())).to_ast()
