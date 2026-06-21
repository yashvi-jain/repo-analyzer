import hashlib
from pathlib import Path

import lizard
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

# Supported languages
PYTHON_EXTENSIONS = {".py"}

LIZARD_EXTENSIONS = {
    ".cpp",
    ".cc",
    ".c",
    ".hpp",
    ".h",
    ".java",
    ".js",
    ".ts",
}

# -------------------------------------------------------
# File Cache
# -------------------------------------------------------
FINGERPRINT_CACHE = {}
FILE_CACHE = {}
# -------------------------------------------------------
# Helpers
# -------------------------------------------------------

def read_file(file_path: str) -> str:
    """
    Reads a file once and caches it.
    """

    if file_path in FILE_CACHE:
        return FILE_CACHE[file_path]

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as f:

            content = f.read()

            FILE_CACHE[file_path] = content

            return content

    except Exception:

        FILE_CACHE[file_path] = ""

        return ""


def count_lines(file_path: str):
    """
    Counts lines using cached source.
    """

    source = read_file(file_path)

    if not source:
        return 0

    return source.count("\n") + 1

# -------------------------------------------------------
# Normalization
# -------------------------------------------------------

def normalize(value, maximum):
    """
    Normalize a value to 0-100.
    """

    if maximum <= 0:
        return 0.0

    return round((value / maximum) * 100, 2)

# -------------------------------------------------------
# Cyclomatic Complexity
# -------------------------------------------------------

def python_complexity(source: str) -> float:
    """
    Average cyclomatic complexity for Python.
    """

    try:

        results = cc_visit(source)

        if not results:
            return 1.0

        total = sum(obj.complexity for obj in results)

        return round(total / len(results), 2)

    except Exception:
        return 1.0


def other_language_complexity(file_path: str) -> float:
    """
    Uses Lizard for C/C++/Java/JS/TS.
    """

    try:

        analysis = lizard.analyze_file(file_path)

        if not analysis.function_list:
            return 1.0

        total = sum(
            func.cyclomatic_complexity
            for func in analysis.function_list
        )

        return round(
            total / len(analysis.function_list),
            2,
        )

    except Exception:
        return 1.0


def calculate_complexity(file_path: str):
    """
    Dispatch based on language.
    """

    extension = Path(file_path).suffix.lower()

    if extension in PYTHON_EXTENSIONS:

        source = read_file(file_path)

        return python_complexity(source)

    elif extension in LIZARD_EXTENSIONS:

        return other_language_complexity(file_path)

    return 0.0


# -------------------------------------------------------
# Maintainability Index
# -------------------------------------------------------

def calculate_maintainability(file_path: str):
    """
    Radon MI for Python.
    Returns None for unsupported languages.
    """

    extension = Path(file_path).suffix.lower()

    if extension not in PYTHON_EXTENSIONS:
        return None

    source = read_file(file_path)

    try:

        score = mi_visit(source, multi=True)

        return round(score, 2)

    except Exception:

        return None


# -------------------------------------------------------
# Utility
# -------------------------------------------------------

def file_hash(file_path: str):
    """
    SHA256 hash used later for duplicate detection.
    """

    source = read_file(file_path)

    return hashlib.sha256(
        source.encode("utf-8")
    ).hexdigest()

import re
from collections import defaultdict


# -------------------------------------------------------
# Language Detection
# -------------------------------------------------------

LANGUAGE_MAP = {
    ".py": "Python",
    ".cpp": "C++",
    ".cc": "C++",
    ".c": "C",
    ".hpp": "C++",
    ".h": "C/C++ Header",
    ".java": "Java",
    ".js": "JavaScript",
    ".ts": "TypeScript",
}


def detect_language(file_path: str):
    """
    Detect programming language from extension.
    """

    extension = Path(file_path).suffix.lower()

    return LANGUAGE_MAP.get(extension, "Unknown")


# -------------------------------------------------------
# Tokenization
# -------------------------------------------------------

def tokenize(source: str):
    """
    Removes comments, whitespace and symbols.
    Used for duplicate detection.
    """

    source = re.sub(r"//.*", "", source)
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    source = re.sub(r"#.*", "", source)

    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", source)

    return tokens

# -------------------------------------------------------
# Fingerprinting
# -------------------------------------------------------

def fingerprints(source: str):
    """
    Returns cached fingerprints.
    """

    cache_key = hashlib.sha256(
        source.encode()
    ).hexdigest()

    if cache_key in FINGERPRINT_CACHE:
        return FINGERPRINT_CACHE[cache_key]

    tokens = tokenize(source)

    k = 5

    if len(tokens) < k:

        FINGERPRINT_CACHE[cache_key] = set()

        return set()

    prints = set()

    for i in range(len(tokens) - k + 1):

        gram = " ".join(tokens[i:i + k])

        prints.add(
            hashlib.sha256(
                gram.encode()
            ).hexdigest()
        )

    FINGERPRINT_CACHE[cache_key] = prints

    return prints


def jaccard_similarity(a, b):
    """
    Jaccard similarity between fingerprint sets.
    """

    if not a or not b:
        return 0

    return (
        len(a & b)
        /
        len(a | b)
    )

# -------------------------------------------------------
# Duplicate Detection
# -------------------------------------------------------

def duplicate_percentage(file_path, all_files):
    """
    Duplicate percentage using fingerprint similarity.
    """

    current = fingerprints(
        read_file(file_path)
    )

    best = 0

    for other in all_files:

        if other == file_path:
            continue

        score = jaccard_similarity(
            current,
            fingerprints(
                read_file(other)
            )
        )

        best = max(best, score)

    return round(best * 100, 2)

def duplicate_clusters(all_files):
    """
    Groups highly similar files.
    """

    clusters = []

    visited = set()

    for file in all_files:

        if file in visited:
            continue

        group = [file]

        visited.add(file)

        fp1 = fingerprints(
            read_file(file)
        )

        for other in all_files:

            if other == file:
                continue

            if other in visited:
                continue

            fp2 = fingerprints(
                read_file(other)
            )

            similarity = jaccard_similarity(
                fp1,
                fp2,
            )

            if similarity >= 0.80:

                group.append(other)

                visited.add(other)

        if len(group) > 1:
            clusters.append(group)

    return clusters


# -------------------------------------------------------
# Python Dead Code
# -------------------------------------------------------

def detect_dead_python(source: str):
    """
    Very lightweight dead-code detection.

    Flags:
    - functions never called
    """

    functions = re.findall(
        r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",
        source,
    )

    dead = []

    for function in functions:

        occurrences = len(
            re.findall(
                rf"\b{function}\b",
                source,
            )
        )

        if occurrences == 1:
            dead.append(function)

    return dead


# -------------------------------------------------------
# C/C++ Unused Includes
# -------------------------------------------------------

def detect_unused_includes(source: str):
    """
    Simple heuristic.

    Detects headers that never appear again.
    """

    includes = re.findall(
        r'#include\s+[<"](.+?)[>"]',
        source,
    )

    unused = []

    for header in includes:

        keyword = (
            header
            .split("/")[-1]
            .split(".")[0]
        )

        body = source.split("\n")

        body = "\n".join(body[1:])

        if keyword not in body:
            unused.append(header)

    return unused


# -------------------------------------------------------
# Dead Code Dispatcher
# -------------------------------------------------------

def dead_code_report(file_path: str):

    source = read_file(file_path)

    extension = Path(file_path).suffix.lower()

    if extension == ".py":

        return {
            "unused_functions": detect_dead_python(source)
        }

    elif extension in {
        ".cpp",
        ".cc",
        ".c",
        ".hpp",
        ".h",
    }:

        return {
            "unused_includes": detect_unused_includes(source)
        }

    return {}

from git import Repo

# -------------------------------------------------------
# Git Churn
# -------------------------------------------------------

def file_churn(repo_path: str):
    """
    Number of commits touching every file.
    """

    repo = Repo(repo_path)

    churn = defaultdict(int)

    try:

        commits = list(repo.iter_commits())

        for commit in commits:

            if not commit.parents:
                continue

            parent = commit.parents[0]

            diff = parent.diff(commit)

            for change in diff:

                if change.b_path:

                    churn[change.b_path] += 1

    except Exception:
        pass

    return churn


# -------------------------------------------------------
# Risk Score
# -------------------------------------------------------

def calculate_risk_score(
    complexity,
    maintainability,
    duplicate_percent,
    churn,
    coupling,
    lines,
):
    """
    Production-style engineering risk score.
    """

    complexity_score = min(complexity * 8, 100)

    maintainability_penalty = (
        50
        if maintainability is None
        else 100 - maintainability
    )

    churn_score = min(churn * 5, 100)

    size_score = size_penalty(lines)

    score = (

        0.25 * complexity_score

        + 0.20 * churn_score

        + 0.20 * maintainability_penalty

        + 0.15 * duplicate_percent

        + 0.10 * coupling

        + 0.10 * size_score

    )

    return round(min(score, 100), 2)


# -------------------------------------------------------
# Hotspots
# -------------------------------------------------------

def hotspot_score(
    complexity,
    churn,
):
    """
    Higher means more attention required.
    """

    return round(complexity * max(churn, 1), 2)

# -------------------------------------------------------
# File Size Penalty
# -------------------------------------------------------

def size_penalty(lines):
    """
    Penalize large source files.
    """

    if lines < 300:
        return 0

    if lines < 500:
        return 20

    if lines < 800:
        return 50

    return 100


# -------------------------------------------------------
# Coupling Penalty
# -------------------------------------------------------

def coupling_penalty(graph, file_path):
    """
    Fan-in + Fan-out penalty.
    """

    if graph is None:
        return 0

    fan_in = graph.in_degree(file_path)

    fan_out = graph.out_degree(file_path)

    coupling = fan_in + fan_out

    return min(coupling * 10, 100)

# -------------------------------------------------------
# Repository Code Health
# -------------------------------------------------------

def code_health(metrics):

    if not metrics:
        return 100.0

    avg_complexity = (
        sum(m["complexity"] for m in metrics)
        / len(metrics)
    )

    maintainability = [

        m["maintainability"]

        for m in metrics

        if m["maintainability"] is not None
    ]

    duplicates = [
        m["duplicate"]
        for m in metrics
    ]

    risk = [
        m["risk"]
        for m in metrics
    ]

    avg_mi = (
        sum(maintainability) / len(maintainability)
        if maintainability
        else 50
    )

    avg_duplicate = (
        sum(duplicates) / len(duplicates)
    )

    avg_risk = (
        sum(risk) / len(risk)
    )

    health = (
        100
        - avg_complexity * 2
        + avg_mi * 0.45
        - avg_duplicate * 0.20
        - avg_risk * 0.30
    )

    return round(
        max(0, min(100, health)),
        2,
    )


# -------------------------------------------------------
# Grade
# -------------------------------------------------------

def health_grade(score):

    if score >= 90:
        return "A"

    if score >= 80:
        return "B"

    if score >= 70:
        return "C"

    if score >= 60:
        return "D"

    return "F"


# -------------------------------------------------------
# Repository Summary
# -------------------------------------------------------

def repository_summary(metrics):

    if not metrics:

        return {
            "average_complexity": 0,
            "average_maintainability": 0,
            "average_risk": 0,
            "code_health": 100,
            "grade": "A",
        }

    complexity = sum(
        m["complexity"]
        for m in metrics
    ) / len(metrics)

    maintainability = [

        m["maintainability"]

        for m in metrics

        if m["maintainability"] is not None
    ]

    risk = sum(
        m["risk"]
        for m in metrics
    ) / len(metrics)

    mi = (
        sum(maintainability)
        / len(maintainability)
        if maintainability
        else 0
    )

    health = code_health(metrics)

    return {

        "average_complexity": round(complexity, 2),

        "average_maintainability": round(mi, 2),

        "average_risk": round(risk, 2),

        "code_health": health,

        "grade": health_grade(health),
    }

# -------------------------------------------------------
# Complete Repository Analysis
# -------------------------------------------------------

def analyze_file(file, repo_path, source_files, churn, dependency_graph):

    relative_path = file

    coupling = coupling_penalty(
        dependency_graph,
        file,
    )

    complexity = calculate_complexity(file)
    maintainability = calculate_maintainability(file)
    duplicate = duplicate_percentage(file, source_files)

    lines = count_lines(file)

    commits = churn.get(
        relative_path.replace("\\", "/"),
        0,
    )

    hotspot = hotspot_score(
        complexity,
        commits,
    )

    risk = calculate_risk_score(
        complexity,
        maintainability,
        duplicate,
        commits,
        coupling=coupling,
        lines=lines
    )

    return {

        "file": relative_path,
        "language": detect_language(file),
        "lines": lines,
        "complexity": complexity,
        "maintainability": maintainability,
        "duplicate": duplicate,
        "risk": risk,
        "hotspot": hotspot,
        "git_churn": commits,
        "dead_code": dead_code_report(file),
    }

def analyze_repository(repo_path: str, source_files, dependency_graph):
    """
    Analyze every source file in the repository.

    Returns:
    {
        "summary": ...,
        "files": ...
    }
    """
    FILE_CACHE.clear()
    FINGERPRINT_CACHE.clear()

    churn = file_churn(repo_path)

    metrics = []

    with ThreadPoolExecutor() as executor:

        metrics = list(

            executor.map(

                lambda f: analyze_file(
                    f,
                    repo_path,
                    source_files,
                    churn,
                    dependency_graph,
                ),

                source_files,

            )

        )

    metrics.sort(
        key=lambda x: x["risk"],
        reverse=True,
    )

    return {

        "summary": repository_summary(metrics),

        "files": metrics,
    }