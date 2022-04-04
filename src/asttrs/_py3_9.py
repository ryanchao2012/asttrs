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
    type_ignores: LIST["type_ignore"] = attr.ib(factory=list)


@immutable
class Interactive(mod):
    body: LIST["stmt"] = attr.ib(factory=list)


@immutable
class Expression(mod):
    body: "expr"


@immutable
class FunctionType(mod):
    argtypes: LIST["expr"] = attr.ib(factory=list)
    returns: "expr"


class stmt(AST):
    pass


@immutable
class FunctionDef(stmt):
    """
    A function definition.
    * ``name`` is a raw string of the function name.
    * ``args`` is an :class:`arguments` node.
    * ``body`` is the list of nodes inside the function.
    * ``decorator_list`` is the list of decorators to be applied, stored outermost
    first (i.e. the first in the list will be applied last).
    * ``returns`` is the return annotation.
    .. attribute:: type_comment
    ``type_comment`` is an optional string with the type annotation as a comment.
    """

    name: "identifier"
    args: "arguments"
    body: LIST["stmt"] = attr.ib(factory=list)
    decorator_list: LIST["expr"] = attr.ib(factory=list)
    returns: "expr" = None
    type_comment: "string" = None


@immutable
class AsyncFunctionDef(stmt):
    """
    An ``async def`` function definition. Has the same fields as
    :class:`FunctionDef`.
    """

    name: "identifier"
    args: "arguments"
    body: LIST["stmt"] = attr.ib(factory=list)
    decorator_list: LIST["expr"] = attr.ib(factory=list)
    returns: "expr" = None
    type_comment: "string" = None


@immutable
class ClassDef(stmt):
    """
    A class definition.
    * ``name`` is a raw string for the class name
    * ``bases`` is a list of nodes for explicitly specified base classes.
    * ``keywords`` is a list of :class:`keyword` nodes, principally for 'metaclass'.
    Other keywords will be passed to the metaclass, as per `PEP-3115
    <https://www.python.org/dev/peps/pep-3115/>`_.
    * ``starargs`` and ``kwargs`` are each a single node, as in a function call.
    starargs will be expanded to join the list of base classes, and kwargs will
    be passed to the metaclass.
    * ``body`` is a list of nodes representing the code within the class
    definition.
    * ``decorator_list`` is a list of nodes, as in :class:`FunctionDef`.

    Examples:

    >>> Module(
    ...     body=[
    ...         ClassDef(
    ...             name='Foo',
    ...             bases=[
    ...                 Name(id='base1', ctx=Load()),
    ...                 Name(id='base2', ctx=Load())],
    ...             keywords=[
    ...                 keyword(
    ...                     arg='metaclass',
    ...                     value=Name(id='meta', ctx=Load()))],
    ...             body=[
    ...                 Pass()],
    ...             decorator_list=[
    ...                 Name(id='decorator1', ctx=Load()),
    ...                 Name(id='decorator2', ctx=Load())])],
    ...     type_ignores=[]).show()
    @decorator1
    @decorator2
    class Foo(base1, base2, metaclass=meta):
        pass
    """

    name: "identifier"
    bases: LIST["expr"] = attr.ib(factory=list)
    keywords: LIST["keyword"] = attr.ib(factory=list)
    body: LIST["stmt"] = attr.ib(factory=list)
    decorator_list: LIST["expr"] = attr.ib(factory=list)


@immutable
class Return(stmt):
    """
    A ``return`` statement.

    Examples:

    >>> Module(
    ...     body=[
    ...         Return(
    ...             value=Constant(value=4))],
    ...     type_ignores=[]).show()
    return 4
    """

    value: "expr" = None


@immutable
class Delete(stmt):
    """
    Represents a ``del`` statement. ``targets`` is a list of nodes, such as
    :class:`Name`, :class:`Attribute` or :class:`Subscript` nodes.

    Examples:

    >>> Module(
    ...     body=[
    ...         Delete(
    ...             targets=[
    ...                 Name(id='x', ctx=Del()),
    ...                 Name(id='y', ctx=Del()),
    ...                 Name(id='z', ctx=Del())])],
    ...     type_ignores=[]).show()
    del x, y, z
    """

    targets: LIST["expr"] = attr.ib(factory=list)


@immutable
class Assign(stmt):
    """
    An assignment. ``targets`` is a list of nodes, and ``value`` is a single node.
    Multiple nodes in ``targets`` represents assigning the same value to each.
    Unpacking is represented by putting a :class:`Tuple` or :class:`List`
    within ``targets``.
    .. attribute:: type_comment
    ``type_comment`` is an optional string with the type annotation as a comment.

    Examples:

    >>> Module(
    ...     body=[
    ...         Assign(
    ...             targets=[
    ...                 Name(id='a', ctx=Store()),
    ...                 Name(id='b', ctx=Store())],
    ...             value=Constant(value=1))],
    ...     type_ignores=[]).show()
    a = b = 1

    >>> Module(
    ...     body=[
    ...         Assign(
    ...             targets=[
    ...                 Tuple(
    ...                     elts=[
    ...                         Name(id='a', ctx=Store()),
    ...                         Name(id='b', ctx=Store())],
    ...                     ctx=Store())],
    ...             value=Name(id='c', ctx=Load()))],
    ...     type_ignores=[]).show()
    a, b = c
    """

    targets: LIST["expr"] = attr.ib(factory=list)
    value: "expr"
    type_comment: "string" = None


@immutable
class AugAssign(stmt):
    """
    Augmented assignment, such as ``a += 1``. In the following example,
    ``target`` is a :class:`Name` node for ``x`` (with the :class:`Store`
    context), ``op`` is :class:`Add`, and ``value`` is a :class:`Constant` with
    value for 1.
    The ``target`` attribute connot be of class :class:`Tuple` or :class:`List`,
    unlike the targets of :class:`Assign`.

    Examples:

    >>> Module(
    ...     body=[
    ...         AugAssign(
    ...             target=Name(id='x', ctx=Store()),
    ...             op=Add(),
    ...             value=Constant(value=2))],
    ...     type_ignores=[]).show()
    x += 2
    """

    target: "expr"
    op: "operator"
    value: "expr"


@immutable
class AnnAssign(stmt):
    """
    An assignment with a type annotation. ``target`` is a single node and can
    be a :class:`Name`, a :class:`Attribute` or a :class:`Subscript`.
    ``annotation`` is the annotation, such as a :class:`Constant` or :class:`Name`
    node. ``value`` is a single optional node. ``simple`` is a boolean integer
    set to True for a :class:`Name` node in ``target`` that do not appear in
    between parenthesis and are hence pure names and not expressions.

    Examples:

    >>> Module(
    ...     body=[
    ...         AnnAssign(
    ...             target=Name(id='c', ctx=Store()),
    ...             annotation=Name(id='int', ctx=Load()),
    ...             simple=1)],
    ...     type_ignores=[]).show()
    c: int

    >>> Module(
    ...     body=[
    ...         AnnAssign(
    ...             target=Name(id='a', ctx=Store()),
    ...             annotation=Name(id='int', ctx=Load()),
    ...             value=Constant(value=1),
    ...             simple=0)],
    ...     type_ignores=[]).show()
    (a): int = 1

    >>> Module(
    ...     body=[
    ...         AnnAssign(
    ...             target=Attribute(
    ...                 value=Name(id='a', ctx=Load()),
    ...                 attr='b',
    ...                 ctx=Store()),
    ...             annotation=Name(id='int', ctx=Load()),
    ...             simple=0)],
    ...     type_ignores=[]).show()
    a.b: int

    >>> Module(
    ...     body=[
    ...         AnnAssign(
    ...             target=Subscript(
    ...                 value=Name(id='a', ctx=Load()),
    ...                 slice=Constant(value=1),
    ...                 ctx=Store()),
    ...             annotation=Name(id='int', ctx=Load()),
    ...             simple=0)],
    ...     type_ignores=[]).show()
    a[1]: int
    """

    target: "expr"
    annotation: "expr"
    value: "expr" = None
    simple: "int"


@immutable
class For(stmt):
    """
    A ``for`` loop. ``target`` holds the variable(s) the loop assigns to, as a
    single :class:`Name`, :class:`Tuple` or :class:`List` node. ``iter`` holds
    the item to be looped over, again as a single node. ``body`` and ``orelse``
    contain lists of nodes to execute. Those in ``orelse`` are executed if the
    loop finishes normally, rather than via a ``break`` statement.
    .. attribute:: type_comment
    ``type_comment`` is an optional string with the type annotation as a comment.

    Examples:

    >>> Module(
    ...     body=[
    ...         For(
    ...             target=Name(id='x', ctx=Store()),
    ...             iter=Name(id='y', ctx=Load()),
    ...             body=[
    ...                 Expr(
    ...                     value=Constant(value=Ellipsis))],
    ...             orelse=[
    ...                 Expr(
    ...                     value=Constant(value=Ellipsis))])],
    ...     type_ignores=[]).show()
    for x in y:
        ...
    else:
        ...
    """

    target: "expr"
    iter: "expr"
    body: LIST["stmt"] = attr.ib(factory=list)
    orelse: LIST["stmt"] = attr.ib(factory=list)
    type_comment: "string" = None


@immutable
class AsyncFor(stmt):
    """
    ``async for`` loops and ``async with`` context managers. They have the same
    fields as :class:`For` and :class:`With`, respectively. Only valid in the
    body of an :class:`AsyncFunctionDef`.
    """

    target: "expr"
    iter: "expr"
    body: LIST["stmt"] = attr.ib(factory=list)
    orelse: LIST["stmt"] = attr.ib(factory=list)
    type_comment: "string" = None


@immutable
class While(stmt):
    """
    A ``while`` loop. ``test`` holds the condition, such as a :class:`Compare`
    node.

    Examples:

    >>> Module(
    ...     body=[
    ...         For(
    ...             target=Name(id='a', ctx=Store()),
    ...             iter=Name(id='b', ctx=Load()),
    ...             body=[
    ...                 If(
    ...                     test=Compare(
    ...                         left=Name(id='a', ctx=Load()),
    ...                         ops=[
    ...                             Gt()],
    ...                         comparators=[
    ...                             Constant(value=5)]),
    ...                     body=[
    ...                         Break()],
    ...                     orelse=[
    ...                         Continue()])],
    ...             orelse=[])],
    ...     type_ignores=[]).show()
    for a in b:
        if a > 5:
            break
        else:
            continue
    """

    test: "expr"
    body: LIST["stmt"] = attr.ib(factory=list)
    orelse: LIST["stmt"] = attr.ib(factory=list)


@immutable
class If(stmt):
    """
    An ``if`` statement. ``test`` holds a single node, such as a :class:`Compare`
    node. ``body`` and ``orelse`` each hold a list of nodes.
    ``elif`` clauses don't have a special representation in the AST, but rather
    appear as extra :class:`If` nodes within the ``orelse`` section of the
    previous one.

    Examples:

    >>> Module(
    ...     body=[
    ...         If(
    ...             test=Name(id='x', ctx=Load()),
    ...             body=[
    ...                 Expr(
    ...                     value=Constant(value=Ellipsis))],
    ...             orelse=[
    ...                 If(
    ...                     test=Name(id='y', ctx=Load()),
    ...                     body=[
    ...                         Expr(
    ...                             value=Constant(value=Ellipsis))],
    ...                     orelse=[
    ...                         Expr(
    ...                             value=Constant(value=Ellipsis))])])],
    ...     type_ignores=[]).show()
    if x:
        ...
    elif y:
        ...
    else:
        ...
    """

    test: "expr"
    body: LIST["stmt"] = attr.ib(factory=list)
    orelse: LIST["stmt"] = attr.ib(factory=list)


@immutable
class With(stmt):
    """
    A ``with`` block. ``items`` is a list of :class:`withitem` nodes representing
    the context managers, and ``body`` is the indented block inside the context.
    .. attribute:: type_comment
    ``type_comment`` is an optional string with the type annotation as a comment.
    """

    items: LIST["withitem"] = attr.ib(factory=list)
    body: LIST["stmt"] = attr.ib(factory=list)
    type_comment: "string" = None


@immutable
class AsyncWith(stmt):
    """
    ``async for`` loops and ``async with`` context managers. They have the same
    fields as :class:`For` and :class:`With`, respectively. Only valid in the
    body of an :class:`AsyncFunctionDef`.
    """

    items: LIST["withitem"] = attr.ib(factory=list)
    body: LIST["stmt"] = attr.ib(factory=list)
    type_comment: "string" = None


@immutable
class Raise(stmt):
    """
    A ``raise`` statement. ``exc`` is the exception object to be raised, normally a
    :class:`Call` or :class:`Name`, or ``None`` for a standalone ``raise``.
    ``cause`` is the optional part for ``y`` in ``raise x from y``.

    Examples:

    >>> Module(
    ...     body=[
    ...         Raise(
    ...             exc=Name(id='x', ctx=Load()),
    ...             cause=Name(id='y', ctx=Load()))],
    ...     type_ignores=[]).show()
    raise x from y
    """

    exc: "expr" = None
    cause: "expr" = None


@immutable
class Try(stmt):
    """
    ``try`` blocks. All attributes are list of nodes to execute, except for
    ``handlers``, which is a list of :class:`ExceptHandler` nodes.

    Examples:

    >>> Module(
    ...     body=[
    ...         Try(
    ...             body=[
    ...                 Expr(
    ...                     value=Constant(value=Ellipsis))],
    ...             handlers=[
    ...                 ExceptHandler(
    ...                     type=Name(id='Exception', ctx=Load()),
    ...                     body=[
    ...                         Expr(
    ...                             value=Constant(value=Ellipsis))]),
    ...                 ExceptHandler(
    ...                     type=Name(id='OtherException', ctx=Load()),
    ...                     name='e',
    ...                     body=[
    ...                         Expr(
    ...                             value=Constant(value=Ellipsis))])],
    ...             orelse=[
    ...                 Expr(
    ...                     value=Constant(value=Ellipsis))],
    ...             finalbody=[
    ...                 Expr(
    ...                     value=Constant(value=Ellipsis))])],
    ...     type_ignores=[]).show()
    try:
        ...
    except Exception:
        ...
    except OtherException as e:
        ...
    else:
        ...
    finally:
        ...
    """

    body: LIST["stmt"] = attr.ib(factory=list)
    handlers: LIST["excepthandler"] = attr.ib(factory=list)
    orelse: LIST["stmt"] = attr.ib(factory=list)
    finalbody: LIST["stmt"] = attr.ib(factory=list)


@immutable
class Assert(stmt):
    """
    An assertion. ``test`` holds the condition, such as a :class:`Compare` node.
    ``msg`` holds the failure message.

    Examples:

    >>> Module(
    ...     body=[
    ...         Assert(
    ...             test=Name(id='x', ctx=Load()),
    ...             msg=Name(id='y', ctx=Load()))],
    ...     type_ignores=[]).show()
    assert x, y
    """

    test: "expr"
    msg: "expr" = None


@immutable
class Import(stmt):
    """
    An import statement. ``names`` is a list of :class:`alias` nodes.

    Examples:

    >>> Module(
    ...     body=[
    ...         Import(
    ...             names=[
    ...                 alias(name='x'),
    ...                 alias(name='y'),
    ...                 alias(name='z')])],
    ...     type_ignores=[]).show()
    import x, y, z
    """

    names: LIST["alias"] = attr.ib(factory=list)


@immutable
class ImportFrom(stmt):
    """
    Represents ``from x import y``. ``module`` is a raw string of the 'from' name,
    without any leading dots, or ``None`` for statements such as ``from . import foo``.
    ``level`` is an integer holding the level of the relative import (0 means
    absolute import).

    Examples:

    >>> Module(
    ...     body=[
    ...         ImportFrom(
    ...             module='y',
    ...             names=[
    ...                 alias(name='x'),
    ...                 alias(name='y'),
    ...                 alias(name='z')],
    ...             level=0)],
    ...     type_ignores=[]).show()
    from y import x, y, z
    """

    module: "identifier" = None
    names: LIST["alias"] = attr.ib(factory=list)
    level: "int" = None


@immutable
class Global(stmt):
    """
    ``global`` and ``nonlocal`` statements. ``names`` is a list of raw strings.
    """

    names: LIST["identifier"] = attr.ib(factory=list)


@immutable
class Nonlocal(stmt):
    """
    ``global`` and ``nonlocal`` statements. ``names`` is a list of raw strings.

    Examples:

    >>> Module(
    ...     body=[
    ...         Global(
    ...             names=[
    ...                 'x',
    ...                 'y',
    ...                 'z'])],
    ...     type_ignores=[]).show()
    global x, y, z

    >>> Module(
    ...     body=[
    ...         Nonlocal(
    ...             names=[
    ...                 'x',
    ...                 'y',
    ...                 'z'])],
    ...     type_ignores=[]).show()
    nonlocal x, y, z
    """

    names: LIST["identifier"] = attr.ib(factory=list)


@immutable
class Expr(stmt):
    """
    When an expression, such as a function call, appears as a statement by itself
    with its return value not used or stored, it is wrapped in this container.
    ``value`` holds one of the other nodes in this section, a :class:`Constant`, a
    :class:`Name`, a :class:`Lambda`, a :class:`Yield` or :class:`YieldFrom` node.

    Examples:

    >>> Module(
    ...     body=[
    ...         Expr(
    ...             value=UnaryOp(
    ...                 op=USub(),
    ...                 operand=Name(id='a', ctx=Load())))],
    ...     type_ignores=[]).show()
    -a
    """

    value: "expr"


class Pass(stmt):
    """
    A ``pass`` statement.

    Examples:

    >>> Module(
    ...     body=[
    ...         Pass()],
    ...     type_ignores=[]).show()
    pass
    """

    pass


class Break(stmt):
    pass


class Continue(stmt):
    pass


class expr(AST):
    pass


@immutable
class BoolOp(expr):
    """
    A boolean operation, 'or' or 'and'. ``op`` is :class:`Or` or :class:`And`.
    ``values`` are the values involved. Consecutive operations with the same
    operator, such as ``a or b or c``, are collapsed into one node with several
    values.
    This doesn't include ``not``, which is a :class:`UnaryOp`.

    Examples:

    >>> Expression(
    ...     body=BoolOp(
    ...         op=Or(),
    ...         values=[
    ...             Name(id='x', ctx=Load()),
    ...             Name(id='y', ctx=Load())])).show()
    (x or y)
    """

    op: "boolop"
    values: LIST["expr"] = attr.ib(factory=list)


@immutable
class NamedExpr(expr):
    """
    A named expression. This AST node is produced by the assignment expressions
    operator (also known as the walrus operator). As opposed to the :class:`Assign`
    node in which the first argument can be multiple nodes, in this case both
    ``target`` and ``value`` must be single nodes.

    Examples:

    >>> Expression(
    ...     body=NamedExpr(
    ...         target=Name(id='x', ctx=Store()),
    ...         value=Constant(value=4))).show()
    (x := 4)
    """

    target: "expr"
    value: "expr"


@immutable
class BinOp(expr):
    """
    A binary operation (like addition or division). ``op`` is the operator, and
    ``left`` and ``right`` are any expression nodes.

    Examples:

    >>> Expression(
    ...     body=BinOp(
    ...         left=Name(id='x', ctx=Load()),
    ...         op=Add(),
    ...         right=Name(id='y', ctx=Load()))).show()
    (x + y)
    """

    left: "expr"
    op: "operator"
    right: "expr"


@immutable
class UnaryOp(expr):
    """
    A unary operation. ``op`` is the operator, and ``operand`` any expression
    node.

    Examples:

    >>> Expression(
    ...     body=UnaryOp(
    ...         op=Not(),
    ...         operand=Name(id='x', ctx=Load()))).show()
    (not x)
    """

    op: "unaryop"
    operand: "expr"


@immutable
class Lambda(expr):
    """
    ``lambda`` is a minimal function definition that can be used inside an
    expression. Unlike :class:`FunctionDef`, ``body`` holds a single node.

    Examples:

    >>> Module(
    ...     body=[
    ...         Expr(
    ...             value=Lambda(
    ...                 args=arguments(
    ...                     posonlyargs=[],
    ...                     args=[
    ...                         arg(arg='x'),
    ...                         arg(arg='y')],
    ...                     kwonlyargs=[],
    ...                     kw_defaults=[],
    ...                     defaults=[]),
    ...                 body=Constant(value=Ellipsis)))],
    ...     type_ignores=[]).show()
    lambda x, y: ...
    """

    args: "arguments"
    body: "expr"


@immutable
class IfExp(expr):
    """
    An expression such as ``a if b else c``. Each field holds a single node, so
    in the following example, all three are :class:`Name` nodes.

    Examples:

    >>> Expression(
    ...     body=IfExp(
    ...         test=Name(id='b', ctx=Load()),
    ...         body=Name(id='a', ctx=Load()),
    ...         orelse=Name(id='c', ctx=Load()))).show()
    (a if b else c)
    """

    test: "expr"
    body: "expr"
    orelse: "expr"


@immutable
class Dict(expr):
    """
    A dictionary. ``keys`` and ``values`` hold lists of nodes representing the
    keys and the values respectively, in matching order (what would be returned
    when calling :code:`dictionary.keys()` and :code:`dictionary.values()`).
    When doing dictionary unpacking using dictionary literals the expression to be
    expanded goes in the ``values`` list, with a ``None`` at the corresponding
    position in ``keys``.

    Examples:

    >>> Expression(
    ...     body=Dict(
    ...         keys=[
    ...             Constant(value='a'),
    ...             None],
    ...         values=[
    ...             Constant(value=1),
    ...             Name(id='d', ctx=Load())])).show()
    {'a': 1, **d}
    """

    keys: LIST["expr"] = attr.ib(factory=list)
    values: LIST["expr"] = attr.ib(factory=list)


@immutable
class Set(expr):
    """
    A set. ``elts`` holds a list of nodes representing the set's elements.

    Examples:

    >>> Expression(
    ...     body=Set(
    ...         elts=[
    ...             Constant(value=1),
    ...             Constant(value=2),
    ...             Constant(value=3)])).show()
    {1, 2, 3}
    """

    elts: LIST["expr"] = attr.ib(factory=list)


@immutable
class ListComp(expr):
    """
    List and set comprehensions, generator expressions, and dictionary
    comprehensions. ``elt`` (or ``key`` and ``value``) is a single node
    representing the part that will be evaluated for each item.
    ``generators`` is a list of :class:`comprehension` nodes.
    """

    elt: "expr"
    generators: LIST["comprehension"] = attr.ib(factory=list)


@immutable
class SetComp(expr):
    """
    List and set comprehensions, generator expressions, and dictionary
    comprehensions. ``elt`` (or ``key`` and ``value``) is a single node
    representing the part that will be evaluated for each item.
    ``generators`` is a list of :class:`comprehension` nodes.
    """

    elt: "expr"
    generators: LIST["comprehension"] = attr.ib(factory=list)


@immutable
class DictComp(expr):
    """
    List and set comprehensions, generator expressions, and dictionary
    comprehensions. ``elt`` (or ``key`` and ``value``) is a single node
    representing the part that will be evaluated for each item.
    ``generators`` is a list of :class:`comprehension` nodes.

    Examples:

    >>> Expression(
    ...     body=ListComp(
    ...         elt=Name(id='x', ctx=Load()),
    ...         generators=[
    ...             comprehension(
    ...                 target=Name(id='x', ctx=Store()),
    ...                 iter=Name(id='numbers', ctx=Load()),
    ...                 ifs=[],
    ...                 is_async=0)])).show()
    [x for x in numbers]

    >>> Expression(
    ...     body=DictComp(
    ...         key=Name(id='x', ctx=Load()),
    ...         value=BinOp(
    ...             left=Name(id='x', ctx=Load()),
    ...             op=Pow(),
    ...             right=Constant(value=2)),
    ...         generators=[
    ...             comprehension(
    ...                 target=Name(id='x', ctx=Store()),
    ...                 iter=Name(id='numbers', ctx=Load()),
    ...                 ifs=[],
    ...                 is_async=0)])).show()
    {x: (x ** 2) for x in numbers}

    >>> Expression(
    ...     body=SetComp(
    ...         elt=Name(id='x', ctx=Load()),
    ...         generators=[
    ...             comprehension(
    ...                 target=Name(id='x', ctx=Store()),
    ...                 iter=Name(id='numbers', ctx=Load()),
    ...                 ifs=[],
    ...                 is_async=0)])).show()
    {x for x in numbers}
    """

    key: "expr"
    value: "expr"
    generators: LIST["comprehension"] = attr.ib(factory=list)


@immutable
class GeneratorExp(expr):
    """
    List and set comprehensions, generator expressions, and dictionary
    comprehensions. ``elt`` (or ``key`` and ``value``) is a single node
    representing the part that will be evaluated for each item.
    ``generators`` is a list of :class:`comprehension` nodes.
    """

    elt: "expr"
    generators: LIST["comprehension"] = attr.ib(factory=list)


@immutable
class Await(expr):
    """
    An ``await`` expression. ``value`` is what it waits for.
    Only valid in the body of an :class:`AsyncFunctionDef`.

    Examples:

    >>> Module(
    ...     body=[
    ...         AsyncFunctionDef(
    ...             name='f',
    ...             args=arguments(
    ...                 posonlyargs=[],
    ...                 args=[],
    ...                 kwonlyargs=[],
    ...                 kw_defaults=[],
    ...                 defaults=[]),
    ...             body=[
    ...                 Expr(
    ...                     value=Await(
    ...                         value=Call(
    ...                             func=Name(id='other_func', ctx=Load()),
    ...                             args=[],
    ...                             keywords=[])))],
    ...             decorator_list=[])],
    ...     type_ignores=[]).show()
    async def f():
        await other_func()
    """

    value: "expr"


@immutable
class Yield(expr):
    """
    A ``yield`` or ``yield from`` expression. Because these are expressions, they
    must be wrapped in a :class:`Expr` node if the value sent back is not used.
    """

    value: "expr" = None


@immutable
class YieldFrom(expr):
    """
    A ``yield`` or ``yield from`` expression. Because these are expressions, they
    must be wrapped in a :class:`Expr` node if the value sent back is not used.

    Examples:

    >>> Module(
    ...     body=[
    ...         Expr(
    ...             value=Yield(
    ...                 value=Name(id='x', ctx=Load())))],
    ...     type_ignores=[]).show()
    yield x

    >>> Module(
    ...     body=[
    ...         Expr(
    ...             value=YieldFrom(
    ...                 value=Name(id='x', ctx=Load())))],
    ...     type_ignores=[]).show()
    yield from x
    """

    value: "expr"


@immutable
class Compare(expr):
    """
    A comparison of two or more values. ``left`` is the first value in the
    comparison, ``ops`` the list of operators, and ``comparators`` the list
    of values after the first element in the comparison.

    Examples:

    >>> Expression(
    ...     body=Compare(
    ...         left=Constant(value=1),
    ...         ops=[
    ...             LtE(),
    ...             Lt()],
    ...         comparators=[
    ...             Name(id='a', ctx=Load()),
    ...             Constant(value=10)])).show()
    (1 <= a < 10)
    """

    left: "expr"
    ops: LIST["cmpop"] = attr.ib(factory=list)
    comparators: LIST["expr"] = attr.ib(factory=list)


@immutable
class Call(expr):
    """
    A function call. ``func`` is the function, which will often be a
    :class:`Name` or :class:`Attribute` object. Of the arguments:
    * ``args`` holds a list of the arguments passed by position.
    * ``keywords`` holds a list of :class:`keyword` objects representing
    arguments passed by keyword.
    When creating a ``Call`` node, ``args`` and ``keywords`` are required, but
    they can be empty lists. ``starargs`` and ``kwargs`` are optional.

    Examples:

    >>> Expression(
    ...     body=Call(
    ...         func=Name(id='func', ctx=Load()),
    ...         args=[
    ...             Name(id='a', ctx=Load()),
    ...             Starred(
    ...                 value=Name(id='d', ctx=Load()),
    ...                 ctx=Load())],
    ...         keywords=[
    ...             keyword(
    ...                 arg='b',
    ...                 value=Name(id='c', ctx=Load())),
    ...             keyword(
    ...                 value=Name(id='e', ctx=Load()))])).show()
    func(a, *d, b=c, **e)
    """

    func: "expr"
    args: LIST["expr"] = attr.ib(factory=list)
    keywords: LIST["keyword"] = attr.ib(factory=list)


@immutable
class FormattedValue(expr):
    """
    Node representing a single formatting field in an f-string. If the string
    contains a single formatting field and nothing else the node can be
    isolated otherwise it appears in :class:`JoinedStr`.
    * ``value`` is any expression node (such as a literal, a variable, or a
    function call).
    * ``conversion`` is an integer:
    * -1: no formatting
    * 115: ``!s`` string formatting
    * 114: ``!r`` repr formatting
    * 97: ``!a`` ascii formatting
    * ``format_spec`` is a :class:`JoinedStr` node representing the formatting
    of the value, or ``None`` if no format was specified. Both
    ``conversion`` and ``format_spec`` can be set at the same time.
    """

    value: "expr"
    conversion: "int" = None
    format_spec: "expr" = None


@immutable
class JoinedStr(expr):
    """
    An f-string, comprising a series of :class:`FormattedValue` and :class:`Constant`
    nodes.

    Examples:

    >>> Expression(
    ...     body=JoinedStr(
    ...         values=[
    ...             Constant(value='sin('),
    ...             FormattedValue(
    ...                 value=Name(id='a', ctx=Load()),
    ...                 conversion=-1),
    ...             Constant(value=') is '),
    ...             FormattedValue(
    ...                 value=Call(
    ...                     func=Name(id='sin', ctx=Load()),
    ...                     args=[
    ...                         Name(id='a', ctx=Load())],
    ...                     keywords=[]),
    ...                 conversion=-1,
    ...                 format_spec=JoinedStr(
    ...                     values=[
    ...                         Constant(value='.3')]))])).show()
    f""\"sin({a}) is {sin(a):.3}""\"
    """

    values: LIST["expr"] = attr.ib(factory=list)


@immutable
class Constant(expr):
    """
    A constant value. The ``value`` attribute of the ``Constant`` literal contains the
    Python object it represents. The values represented can be simple types
    such as a number, string or ``None``, but also immutable container types
    (tuples and frozensets) if all of their elements are constant.

    Examples:

    >>> Expression(
    ...     body=Constant(value=123)).show()
    (123)
    """

    value: "constant"
    kind: "string" = None


@immutable
class Attribute(expr):
    """
    Attribute access, e.g. ``d.keys``. ``value`` is a node, typically a
    :class:`Name`. ``attr`` is a bare string giving the name of the attribute,
    and ``ctx`` is :class:`Load`, :class:`Store` or :class:`Del` according to how
    the attribute is acted on.

    Examples:

    >>> Expression(
    ...     body=Attribute(
    ...         value=Name(id='snake', ctx=Load()),
    ...         attr='colour',
    ...         ctx=Load())).show()
    snake.colour
    """

    value: "expr"
    attr: "identifier"
    ctx: "expr_context"


@immutable
class Subscript(expr):
    """
    A subscript, such as ``l[1]``. ``value`` is the subscripted object
    (usually sequence or mapping). ``slice`` is an index, slice or key.
    It can be a :class:`Tuple` and contain a :class:`Slice`.
    ``ctx`` is :class:`Load`, :class:`Store` or :class:`Del`
    according to the action performed with the subscript.

    Examples:

    >>> Expression(
    ...     body=Subscript(
    ...         value=Name(id='l', ctx=Load()),
    ...         slice=Tuple(
    ...             elts=[
    ...                 Slice(
    ...                     lower=Constant(value=1),
    ...                     upper=Constant(value=2)),
    ...                 Constant(value=3)],
    ...             ctx=Load()),
    ...         ctx=Load())).show()
    l[1:2, 3]
    """

    value: "expr"
    slice: "expr"
    ctx: "expr_context"


@immutable
class Starred(expr):
    """
    A ``*var`` variable reference. ``value`` holds the variable, typically a
    :class:`Name` node. This type must be used when building a :class:`Call`
    node with ``*args``.

    Examples:

    >>> Module(
    ...     body=[
    ...         Assign(
    ...             targets=[
    ...                 Tuple(
    ...                     elts=[
    ...                         Name(id='a', ctx=Store()),
    ...                         Starred(
    ...                             value=Name(id='b', ctx=Store()),
    ...                             ctx=Store())],
    ...                     ctx=Store())],
    ...             value=Name(id='it', ctx=Load()))],
    ...     type_ignores=[]).show()
    a, *b = it
    """

    value: "expr"
    ctx: "expr_context"


@immutable
class Name(expr):
    """
    A variable name. ``id`` holds the name as a string, and ``ctx`` is one of
    the following types.
    """

    id: "identifier"
    ctx: "expr_context"


@immutable
class List(expr):
    """
    A list or tuple. ``elts`` holds a list of nodes representing the elements.
    ``ctx`` is :class:`Store` if the container is an assignment target (i.e.
    ``(x,y)=something``), and :class:`Load` otherwise.
    """

    elts: LIST["expr"] = attr.ib(factory=list)
    ctx: "expr_context"


@immutable
class Tuple(expr):
    """
    A list or tuple. ``elts`` holds a list of nodes representing the elements.
    ``ctx`` is :class:`Store` if the container is an assignment target (i.e.
    ``(x,y)=something``), and :class:`Load` otherwise.

    Examples:

    >>> Expression(
    ...     body=List(
    ...         elts=[
    ...             Constant(value=1),
    ...             Constant(value=2),
    ...             Constant(value=3)],
    ...         ctx=Load())).show()
    [1, 2, 3]

    >>> Expression(
    ...     body=Tuple(
    ...         elts=[
    ...             Constant(value=1),
    ...             Constant(value=2),
    ...             Constant(value=3)],
    ...         ctx=Load())).show()
    (1, 2, 3)
    """

    elts: LIST["expr"] = attr.ib(factory=list)
    ctx: "expr_context"


@immutable
class Slice(expr):
    """
    Regular slicing (on the form ``lower:upper`` or ``lower:upper:step``).
    Can occur only inside the *slice* field of :class:`Subscript`, either
    directly or as an element of :class:`Tuple`.

    Examples:

    >>> Expression(
    ...     body=Subscript(
    ...         value=Name(id='l', ctx=Load()),
    ...         slice=Slice(
    ...             lower=Constant(value=1),
    ...             upper=Constant(value=2)),
    ...         ctx=Load())).show()
    l[1:2]
    """

    lower: "expr" = None
    upper: "expr" = None
    step: "expr" = None


class expr_context(AST):
    pass


class Load(expr_context):
    """
    Variable references can be used to load the value of a variable, to assign
    a new value to it, or to delete it. Variable references are given a context
    to distinguish these cases.
    """

    pass


class Store(expr_context):
    """
    Variable references can be used to load the value of a variable, to assign
    a new value to it, or to delete it. Variable references are given a context
    to distinguish these cases.
    """

    pass


class Del(expr_context):
    """
    Variable references can be used to load the value of a variable, to assign
    a new value to it, or to delete it. Variable references are given a context
    to distinguish these cases.

    Examples:

    >>> Module(
    ...     body=[
    ...         Expr(
    ...             value=Name(id='a', ctx=Load()))],
    ...     type_ignores=[]).show()
    a

    >>> Module(
    ...     body=[
    ...         Assign(
    ...             targets=[
    ...                 Name(id='a', ctx=Store())],
    ...             value=Constant(value=1))],
    ...     type_ignores=[]).show()
    a = 1

    >>> Module(
    ...     body=[
    ...         Delete(
    ...             targets=[
    ...                 Name(id='a', ctx=Del())])],
    ...     type_ignores=[]).show()
    del a
    """

    pass


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
    """
    A single ``except`` clause. ``type`` is the exception type it will match,
    typically a :class:`Name` node (or ``None`` for a catch-all ``except:`` clause).
    ``name`` is a raw string for the name to hold the exception, or ``None`` if
    the clause doesn't have ``as foo``. ``body`` is a list of nodes.

    Examples:

    >>> Module(
    ...     body=[
    ...         Try(
    ...             body=[
    ...                 Expr(
    ...                     value=BinOp(
    ...                         left=Name(id='a', ctx=Load()),
    ...                         op=Add(),
    ...                         right=Constant(value=1)))],
    ...             handlers=[
    ...                 ExceptHandler(
    ...                     type=Name(id='TypeError', ctx=Load()),
    ...                     body=[
    ...                         Pass()])],
    ...             orelse=[],
    ...             finalbody=[])],
    ...     type_ignores=[]).show()
    try:
        a + 1
    except TypeError:
        pass
    """

    type: "expr" = None
    name: "identifier" = None
    body: LIST["stmt"] = attr.ib(factory=list)


@immutable
class arguments(AST):
    posonlyargs: LIST["arg"] = attr.ib(factory=list)
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
    type_comment: "string" = None


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


class type_ignore(AST):
    pass


@immutable
class TypeIgnore(type_ignore):
    lineno: "int"
    tag: "string"
