import pathlib
import subprocess as sp
import sys
import tempfile


def blacking(source_code: str):

    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(source_code)
        fname = f.name

    with sp.Popen(["cat", fname], stdout=sp.PIPE) as p:
        cmd = [sys.executable, "-m", "black", "-q", "-"]
        out = sp.check_output(cmd, stdin=p.stdout)

    try:
        pathlib.Path(fname).unlink()

    except FileNotFoundError:
        pass

    return out.decode()


def isorting(source_code: str):

    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(source_code)
        fname = f.name

    with sp.Popen(["cat", fname], stdout=sp.PIPE) as p:
        cmd = [sys.executable, "-m", "isort", "--profile", "black", "-q", "-"]
        out = sp.check_output(cmd, stdin=p.stdout)

    try:
        pathlib.Path(fname).unlink()

    except FileNotFoundError:
        pass

    return out.decode()
