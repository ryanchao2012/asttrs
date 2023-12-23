from __future__ import annotations

import ast
from doctest import DocTestParser
from doctest import Example as DocExample

import ast_decompiler
from invoke import task

from asttrs._base import Defination, Example
from cpython.Parser.asdl import ASDLParser, Product, Sum


def _assign_default(type_name):
    if type_name in ("int",):
        return 0
    else:
        return None


HEADER = """
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
"""


@task()
def build(
    c, asdl_path="cpython/Parser/Python.asdl", doc_path="cpython/Doc/library/ast.rst"
):
    with open(asdl_path, "r") as f:
        asdl = f.read()

    with open(doc_path, "r") as f:
        doc = f.read()

    parsed = ASDLParser().parse(asdl)
    doctests = DocTestParser().parse(doc)

    examples = {}
    lastkey = None
    for doc in doctests:
        if isinstance(doc, str):
            if doc.strip():
                for el in Defination.iter_from_doc(doc):
                    examples.update({el.name: el})
                    lastkey = el.name

        elif isinstance(doc, DocExample):
            if lastkey in examples:
                exp = ast.parse(doc.source, mode="eval")

                try:
                    want = ast_decompiler.decompile(
                        ast.parse(
                            exp.body.args[0].args[0].args[0].value,
                            mode="eval" if "mode='eval'" in doc.source else "exec",
                        )
                    ).strip()
                except Exception:
                    want = exp.body.args[0].args[0].args[0].value.strip()

                source = doc.want.strip() + ".show()"
                el = examples[lastkey]
                el.examples.append(Example(source=source, want=want))

    print(HEADER)

    for node in parsed.dfns:
        if isinstance(node.value, Sum):
            base = node.name

            cls = ast.ClassDef(
                name=base,
                bases=[ast.Name(id="AST", ctx=ast.Load())],
                body=[ast.Pass()],
                decorator_list=[],
            )

            print(ast_decompiler.decompile(cls))

            for nd in node.value.types:
                name = nd.name
                body = []
                docstring = []
                if name in examples:
                    doc = "\n" + examples[name].docstring + "\n\n"

                    if examples[name].examples:
                        doc += "Examples:\n\n"

                        for ex in examples[name].examples:
                            src = (">>> " + ex.source).replace("\n", "\n... ")

                            doc += src + "\n" + ex.want + "\n\n"

                    docstring.append(ast.Expr(value=ast.Constant(value=doc, kind=None)))

                for fd in nd.fields:
                    # print(">>", fd, fd.type)
                    ann = ast.Constant(value=fd.type, kind=None)
                    value = (
                        # FIXME
                        ast.Constant(value=_assign_default(fd.type), kind=None)
                        if fd.opt
                        else None
                    )

                    if fd.seq:
                        ann = ast.Subscript(
                            value=ast.Name(id="LIST", ctx=ast.Load()),
                            slice=ast.Index(ann),
                            ctx=ast.Load(),
                        )

                        value = ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id="attr", ctx=ast.Load()),
                                attr="ib",
                                ctx=ast.Load(),
                            ),
                            args=[],
                            keywords=[
                                ast.keyword(
                                    arg="factory",
                                    value=ast.Name(id="list", ctx=ast.Load()),
                                )
                            ],
                        )

                    body.append(
                        ast.AnnAssign(
                            target=ast.Name(id=fd.name, ctx=ast.Store()),
                            annotation=ann,
                            value=value,
                            simple=1,
                        )
                    )

                cls = ast.ClassDef(
                    name=name,
                    bases=[ast.Name(id=base, ctx=ast.Load())],
                    body=docstring + (body if body else [ast.Pass()]),
                    decorator_list=[ast.Name(id="immutable")] if body else [],
                )

                print(ast_decompiler.decompile(cls))

        elif isinstance(node.value, Product):
            name = node.name
            base = "AST"
            body = []

            for fd in node.value.fields:
                ann = ast.Constant(value=fd.type, kind=None)
                value = ast.Constant(value=None, kind=None) if fd.opt else None

                if fd.seq:
                    ann = ast.Subscript(
                        value=ast.Name(id="LIST", ctx=ast.Load()),
                        slice=ast.Index(ann),
                        ctx=ast.Load(),
                    )

                    value = ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="attr", ctx=ast.Load()),
                            attr="ib",
                            ctx=ast.Load(),
                        ),
                        args=[],
                        keywords=[
                            ast.keyword(
                                arg="factory",
                                value=ast.Name(id="list", ctx=ast.Load()),
                            )
                        ],
                    )

                body.append(
                    ast.AnnAssign(
                        target=ast.Name(id=fd.name, ctx=ast.Store()),
                        annotation=ann,
                        value=value,
                        simple=1,
                    )
                )

            cls = ast.ClassDef(
                name=name,
                bases=[ast.Name(id=base, ctx=ast.Load())],
                body=body if body else [ast.Pass()],
                decorator_list=[ast.Name(id="immutable")] if body else [],
            )
            print(ast_decompiler.decompile(cls))

        else:
            raise ValueError(node)
