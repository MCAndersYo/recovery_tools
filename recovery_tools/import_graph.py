# import_graph.py

import os
import ast
import networkx as nx
from typing import List, Tuple, Optional

def find_python_modules(root: str, package_name: str) -> List[Tuple[str,str]]:
    """
    Scan `root` for .py files.  
    Returns a list of (module_dotted_name, file_path).
    """
    modules = []
    for directory_path, _, files in os.walk(root):
        for filename in files:
            if not filename.endswith(".py"):
                continue
            full_path = os.path.join(directory_path, filename) #the absolute path to the .py file
            rel_path  = os.path.relpath(full_path, root)[:-3]  # the path from root down to the file, minus the trailing .py
            parts = rel_path.split(os.sep) 
            if parts[-1] == "__init__":
                # it's a package: drop the "__init__" part
                if len(parts) == 1:
                    # top‐level __init__.py
                    mod_name = package_name
                else:
                    # nested package __init__.py → pkg.sub
                    mod_name = package_name + "." + ".".join(parts[:-1])
            else:
                # a normal module file
                mod_name = package_name + "." + ".".join(parts)

            modules.append((mod_name, full_path))
    return modules



def resolve_import_from(node: ast.ImportFrom, current_mod: str, pkg_name: str) -> Optional[str]:
    """
    Given an AST ImportFrom node, find absolute imorts and relative imports.
    Absolute imports return exactly what you wrote after the from.
    Relative imports (in case of dot-notation) calculate “where” that dot‐notation lands by chopping off segments of current_module.
    You always end up with an absolute module name that you can use to create your dependency edge.
    """
    if node.level == 0 and node.module:
        return node.module
    # relative import: e.g. from .subpackage import X
    parts = current_mod.split(".")
    if node.level >= len(parts):
        return None   # skip, rather than fallback
    parent = parts[:-node.level]
    if node.module:
        return ".".join(parent + [node.module])
    return ".".join(parent)


def extract_package_imports(module_name: str, path: str, package_name: str) -> List[Tuple[str, str]]:
    imports = []
    # 1) Read and parse the source file
    src  = open(path, "r", encoding="utf-8").read()
    tree = ast.parse(src, filename=path)

    # 2) Walk every AST node looking for imports
    for node in ast.walk(tree):
        # 2a) Plain `import X` statements
        if isinstance(node, ast.Import):
            for alias in node.names:
                # alias.name might be "zeeguu.model.user" or "os"
                if alias.name.startswith(package_name):
                    # record edge: module_name -> alias.name
                    imports.append((module_name, alias.name))

        # 2b) `from Y import Z` statements
        elif isinstance(node, ast.ImportFrom):
            # figure out the absolute module Y (handles “from .subpkg” too)
            imported = resolve_import_from(node, module_name, package_name)
            # only care about imports inside your target package
            if imported and imported.startswith(package_name):
                # record edge: module_name -> imported
                imports.append((module_name, imported))

    return imports


def build_import_graph(root_pkg_dir: str, package_name: str) -> nx.DiGraph:
    """
    Master function: finds all modules, parses their imports,
    and builds a DiGraph of importer → imported.
    """
    G = nx.DiGraph()

    # 1) find all modules
    modules = find_python_modules(root_pkg_dir, package_name)
    for mod_name, _ in modules:
        G.add_node(mod_name)

    # 2) parse imports and add edges
    for mod_name, path in modules:
        for src, dst in extract_package_imports(mod_name, path, package_name):
            G.add_edge(src, dst)
    return G
