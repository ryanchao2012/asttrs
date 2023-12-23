from asttrs.utils import blacking, isorting


def test_isorting():

    source = "\n".join(["import sys, os", "import os"])
    expected = "\n".join(["import os", "import sys"])

    assert isorting(source).strip() == expected


def test_blacking():

    source = "\n".join(["def foo():", "", "", "", "", "    pass"])
    expected = "\n".join(["def foo():", "    pass"])

    assert blacking(source).strip() == expected
