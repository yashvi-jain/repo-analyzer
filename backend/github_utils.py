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
from dotenv import load_dotenv

REPO_STORAGE = Path(os.getenv("REPO_STORAGE", "repos"))
REPO_STORAGE.mkdir(parents=True, exist_ok=True)

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
        ".jsx",
        ".ts",
        ".tsx",
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
                ".env",
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
        source = Path(file_path).read_text(encoding="utf-8", errors="ignore")

        tree = ast.parse(source)

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):

                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):

                if node.module:
                    imports.append(node.module)

    except Exception as e:
        print(file_path, e)

    return imports

def cpp_includes(file_path: str):
    """
    Extract C/C++ includes.
    """

    includes = []

    try:
        source = Path(file_path).read_text(encoding="utf-8", errors="ignore")

        includes = re.findall(r'#include\s+[<"](.+?)[>"]', source)

    except Exception as e:
        print(file_path, e)

    return includes

def js_imports(file_path: str):
    """
    Extracts JavaScript/JSX/TypeScript imports by matching paths inside quotes.
    """
    imports = []
    try:
        source = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        
        source = source.replace("\xa0", " ")
        
        matches = re.findall(r'(?:from|require)\s*\(?\s*[\'"](.+?)[\'"]', source)
        
        for path in matches:
            clean_path = path.replace("\\", "/")
            pure_name = clean_path.split("/")[-1].split(".")[0]
            imports.append(pure_name.strip().lower())

    except Exception as e:
        print(file_path, e)
    return imports

def build_dependency_graph(repo_path, files):
    """
    Builds an actual dependency graph by cross-referencing file stems.
    """
    graph = nx.DiGraph()

    file_lookup = {}
    for file in files:
        graph.add_node(file)
        normalized_path = file.replace("\\", "/")
        pure_name = normalized_path.split("/")[-1].split(".")[0].strip().lower()
        file_lookup[pure_name] = file

    for file in files:
        extension = Path(file).suffix.lower()
        dependencies = []

        if extension == ".py":
  
            raw_py = python_imports(os.path.join(repo_path, file))
            dependencies = [d.split(".")[-1].strip().lower() for d in raw_py]

        elif extension in {
            ".js",
            ".jsx", 
            ".ts", 
            ".tsx"
        }:
            raw_js = js_imports(os.path.join(repo_path, file))
            dependencies = [d.lower() for d in raw_js]

        elif extension in {
            ".cpp", 
            ".cc", 
            ".c", 
            ".hpp", 
            ".h"
        }:
            raw_cpp = cpp_imports(os.path.join(repo_path, file))
            dependencies = [d.split(".")[0].strip().lower() for d in raw_cpp]

        for dep in dependencies:
            if dep in file_lookup:
                target_file = file_lookup[dep]
                if file != target_file:
                    graph.add_edge(file, target_file)

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

def analyze_readme(repo_path: str):
    """
    Analyze README completeness based on common documentation headings.
    """

    readme_path = None

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.lower() == "readme.md":
                readme_path = os.path.join(root, file)
                break
        if readme_path:
            break

    section_keywords = {
        "Installation/Requirements": [
            "installation",
            "install",
            "setup",
            "requirements",
            "prerequisites",
            "supporting",
        ],
        "Usage": [
            "getting started",
            "quick start",
            "usage",
            "how to",
            "how to use",
            "example",
            "examples",
            "run",
        ],
        "Features/Description": [
            "features",
            "capabilities",
            "highlights",
            "summary",
            "functionality",
            "description",
        ],
        "License/Contribution": [
            "license",
            "licence",
            "contributing",
            "contribution",
            "development",
        ],
    }

    if readme_path is None:
        return {
            "exists": False,
            "score": 0,
            "missing_sections": list(section_keywords.keys()),
        }

    try:
        content = Path(readme_path).read_text(
            encoding="utf-8",
            errors="ignore",
        ).lower()
    except Exception:
        return {
            "exists": False,
            "score": 0,
            "missing_sections": "Error analyzing the file",
        }

    headings = re.findall(
        r"^\s*#{1,6}\s+(.*)$",
        content,
        flags=re.MULTILINE,
    )

    headings = [heading.strip() for heading in headings]

    found = []

    for section, keywords in section_keywords.items():
        if any(
            any(keyword in heading for keyword in keywords)
            for heading in headings
        ):
            found.append(section)

    missing = [
        section
        for section in section_keywords
        if section not in found
    ]

    score = round((len(found) / len(section_keywords)) * 100)

    return {
        "exists": True,
        "score": score,
        "missing_sections": missing,
    }