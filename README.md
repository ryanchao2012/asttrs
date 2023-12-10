# asttrs
A attrs-style wrapper for python ast


## Features

### 1. Developer-friendly version of `ast`, 1) easier to access docstring and 2) easier to do codegen.


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


# Then we can easily know how to build a function
from asttrs import arguments, Return, Constant

func = FunctionDef(name="foo", args=arguments(), body=[Return(value=Constant(value="Hello World"))])

print(func.to_source())
# def foo():
#     return 'Hello World'
#

```

### 2. provide `Comment` to codegen comments

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
$ poetry run inv build | poetry run black - >! src/asttrs/_py3_11.py

# run testing
$ poetry run pytest --doctest-modules --cov=src --cov-report=term-missing tests
```