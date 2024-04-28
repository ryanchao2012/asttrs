![](https://github.com/ryanchao2012/asttrs/actions/workflows/asttrs-run-unittests.yml/badge.svg)
![](https://img.shields.io/pypi/v/asttrs.svg)
![](https://img.shields.io/pypi/pyversions/asttrs)
![](https://img.shields.io/github/license/ryanchao2012/asttrs)

# asttrs
A attrs-style wrapper for python ast


## Features

### Developer-friendly version of `ast`
1. easier to access docstring.
2. easier to do codegen.

```python
from ast import FunctionDef

help(FunctionDef)
# Help on class FunctionDef in module ast:

# class FunctionDef(stmt)
#  |  FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list, expr? returns, string? type_comment)
#  |  
#  |  (no docstring)
#  |  
#  |  Method resolution order:
#  |      FunctionDef
#  |      stmt
#  |      AST
#  |      builtins.object
#  |  
#  :
```

vs

```python
from asttrs import FunctionDef

help(FunctionDef)
# Help on class FunctionDef in module asttrs._py3_11:

# class FunctionDef(stmt)
#  |  FunctionDef(*, name: 'identifier', args: 'arguments', body: List[ForwardRef('stmt')] = NOTHING, de
# corator_list: List[ForwardRef('expr')] = NOTHING, returns: 'expr' = None, type_comment: 'string' = Non
# e) -> None
#  |  
#  |  A function definition.
#  |  * ``name`` is a raw string of the function name.
#  |  * ``args`` is an :class:`arguments` node.
#  |  * ``body`` is the list of nodes inside the function.
#  |  * ``decorator_list`` is the list of decorators to be applied, stored outermost
#  |  first (i.e. the first in the list will be applied last).
#  |  * ``returns`` is the return annotation.
#  |  .. attribute:: type_comment
#  |  ``type_comment`` is an optional string with the type annotation as a comment.
#  :


# It's easier to know how to build a function
from asttrs import arguments, Return, Constant

func = FunctionDef(name="foo", args=arguments(), body=[Return(value=Constant(value="Hello World"))])

print(func.to_source())
# def foo():
#     return 'Hello World'
#

```

### Provide `Comment` to codegen comments

```python
from asttrs import Comment


comment = Comment(body="This is a comment,\nsecond line,\nthird line.")
print(comment.to_souce())
# This is a comment,
# second line,
# third line.
```


## Development

```
# switch python version and environment
$ (cd cpython; git checkout v3.11.7) 
$ ln -vsfT .venv311 .venv

# run codegen based on Python.asdl
$ pdm run inv build | pdm run black - >! src/asttrs/_py3_11.py

# run testing
$ pdm run pytest --doctest-modules --cov=asttrs._py3_11 --cov-report=term-missing src/asttrs/_py3_11.py tests
```