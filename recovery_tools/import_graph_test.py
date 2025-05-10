import os
import ast
import tempfile
import shutil
import sys
from pathlib import Path

from import_graph import (
    find_python_modules,
    resolve_import_from,
    extract_package_imports
)

def test_find_python_modules():
    root = tempfile.mkdtemp()
    pkg_name = "pkg"
    # Create structure:
    # root/__init__.py
    # root/a.py
    # root/sub/__init__.py
    # root/sub/b.py
    os.makedirs(os.path.join(root, "sub"))
    open(os.path.join(root, "__init__.py"), "w").close()
    open(os.path.join(root, "a.py"), "w").close()
    open(os.path.join(root, "sub", "__init__.py"), "w").close()
    open(os.path.join(root, "sub", "b.py"), "w").close()

    modules = sorted(find_python_modules(root, pkg_name))
    expected = sorted([
        ("pkg",      os.path.join(root, "__init__.py")),
        ("pkg.a",    os.path.join(root, "a.py")),
        ("pkg.sub",  os.path.join(root, "sub", "__init__.py")),
        ("pkg.sub.b",os.path.join(root, "sub", "b.py")),
    ])
    assert modules == expected, f"Got {modules}, expected {expected}"
    shutil.rmtree(root)

def test_resolve_import_from():
    # Absolute import
    node = ast.ImportFrom(module="zeeguu.model", names=[ast.alias("User", None)], level=0)
    assert resolve_import_from(node, "zeeguu.api.session", "zeeguu") == "zeeguu.model"

    # Relative import: from .user import start
    node = ast.ImportFrom(module="user", names=[ast.alias("start", None)], level=1)
    assert resolve_import_from(node, "zeeguu.api.session", "zeeguu") == "zeeguu.api.user"

    # Relative import: from ..core import helper
    node = ast.ImportFrom(module="core", names=[ast.alias("helper", None)], level=2)
    assert resolve_import_from(node, "zeeguu.api.session", "zeeguu") == "zeeguu.core"

    # Relative import without module: from .. import settings
    node = ast.ImportFrom(module=None, names=[ast.alias("settings", None)], level=2)
    assert resolve_import_from(node, "zeeguu.api.session", "zeeguu") == "zeeguu"


def test_extract_package_imports(tmp_path):
    # Write a temp file with a variety of imports
    code = """\
import zeeguu.model
import pkg.model
import os
from zeeguu.api import Client
from pkg.api import Client
from .subpkg import helper
from .. import config
        """
    tmp_path = Path(tmp_path)
    src_file = tmp_path / "temp.py"
    src_file.write_text(code)

    imports = extract_package_imports("pkg.temp", str(src_file), "pkg")
    expected_targets = {"pkg.model", "pkg.api", "pkg.subpkg"}
    got_targets = {dst for src, dst in imports}
    assert got_targets == expected_targets, f"Got {got_targets}, expected {expected_targets}"


test_find_python_modules()
test_resolve_import_from()
test_extract_package_imports("..")