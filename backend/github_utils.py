import os
import shutil
import ast
import json
import re
import stat

from pathlib import Path
from urllib.parse import urlparse

from git import Repo, GitCommandError
import networkx as nx


REPO_STORAGE = Path("repos")
REPO_STORAGE.mkdir(exist_ok=True)


def validate_github_url(url: str) -> bool:
    """
    Validates whether the provided URL is a GitHub repository.
    """

    parsed = urlparse(url)

    if parsed.netloc != "github.com":
        return False

    path_parts = parsed.path.strip("/").split("/")

    return len(path_parts) >= 2


def get_repo_name(url: str) -> str:
    """
    Extract repository name from GitHub URL.
    """

    name = url.rstrip("/").split("/")[-1]

    if name.endswith(".git"):
        name = name[:-4]

    return name


def clone_repository(url: str) -> str:
    """
    Clone repository into backend/repos/.
    Existing copy is removed to ensure a fresh analysis.
    """

    if not validate_github_url(url):
        raise ValueError("Invalid GitHub repository URL.")

    repo_name = get_repo_name(url)

    destination = REPO_STORAGE / repo_name

    def handle_remove_readonly(func, path, exc):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    if destination.exists():
        shutil.rmtree(destination, onerror=handle_remove_readonly)

    try:
        Repo.clone_from(url, destination)
    except GitCommandError as e:
        raise RuntimeError(f"Failed to clone repository:\n{e}")

    return str(destination)


def get_all_source_files(repo_path: str):
    """
    Recursively return all supported source files.
    """

    extensions = {
        ".py",
        ".cpp",
        ".cc",
        ".c",
        ".hpp",
        ".h",
        ".java",
        ".js",
        ".ts",
    }

    files = []

    for root, dirs, filenames in os.walk(repo_path):

        # Ignore hidden folders and git metadata
        dirs[:] = [
            d for d in dirs
            if d not in {
                ".git",
                "__pycache__",
                "node_modules",
                "venv",
                ".venv",
            }
        ]

        for file in filenames:

            path = Path(root) / file

            if path.suffix.lower() in extensions:
                files.append(str(path.relative_to(repo_path)))

    return files

# -------------------------------------------------------
# Dependency Graph
# -------------------------------------------------------

def python_imports(file_path: str):
    """
    Extract Python imports using AST.
    """

    imports = []

    try:

        source = Path(file_path).read_text(
            encoding="utf-8",
            errors="ignore"
        )

        tree = ast.parse(source)

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):

                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):

                if node.module:
                    imports.append(node.module)

    except Exception:
        pass

    return imports

def cpp_includes(file_path: str):
    """
    Extract C/C++ includes.
    """

    includes = []

    try:

        source = Path(file_path).read_text(
            encoding="utf-8",
            errors="ignore"
        )

        includes = re.findall(
            r'#include\s+[<"](.+?)[>"]',
            source,
        )

    except Exception:
        pass

    return includes

def build_dependency_graph(files):
    """
    Builds an actual dependency graph.
    """

    graph = nx.DiGraph()

    for file in files:

        graph.add_node(file)

        extension = Path(file).suffix.lower()

        dependencies = []

        if extension == ".py":

            dependencies = python_imports(file)

        elif extension in {
            ".cpp",
            ".cc",
            ".c",
            ".hpp",
            ".h",
        }:

            dependencies = cpp_includes(file)

        for dependency in dependencies:

            graph.add_edge(
                file,
                dependency,
            )

    return graph

def dependency_graph_json(graph):
    """
    Converts NetworkX graph to JSON.
    """

    return json.dumps(

        {

            "nodes": [

                {
                    "id": node
                }

                for node in graph.nodes()

            ],

            "links": [

                {
                    "source": source,
                    "target": target,
                }

                for source, target
                in graph.edges()

            ],

        },

        indent=2,
    )

def get_git_statistics(repo_path: str):
    """
    Collect simple Git statistics.
    """

    repo = Repo(repo_path)

    commits = list(repo.iter_commits())

    contributors = {}

    for commit in commits:

        author = commit.author.name

        contributors[author] = contributors.get(author, 0) + 1

    return {
        "total_commits": len(commits),
        "contributors": contributors,
        "default_branch": repo.active_branch.name,
    }