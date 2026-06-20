import networkx as nx


def risk_level(avg_risk):

    if avg_risk < 25:
        return "Low"

    if avg_risk < 50:
        return "Moderate"

    if avg_risk < 75:
        return "High"

    return "Critical"


def architecture_score(summary, graph):

    score = summary["code_health"]

    cycles = len(list(nx.simple_cycles(graph)))

    score -= min(cycles * 3, 20)

    return round(max(score, 0), 2)


def recommendations(summary, files, graph):

    recommendations = []

    if summary["average_complexity"] > 10:
        recommendations.append(
            "Reduce cyclomatic complexity by refactoring large functions."
        )

    if summary["average_maintainability"] < 70:
        recommendations.append(
            "Improve maintainability by reducing function size and duplication."
        )

    if summary["average_risk"] > 60:
        recommendations.append(
            "Prioritize high-risk files for refactoring."
        )

    cycles = list(nx.simple_cycles(graph))

    if cycles:
        recommendations.append(
            "Resolve circular dependencies between modules."
        )

    if not recommendations:
        recommendations.append(
            "Repository follows good engineering practices."
        )

    return recommendations


def generate_report(summary, files, graph, git_stats):

    hotspots = sorted(
        files,
        key=lambda x: x["hotspot"],
        reverse=True,
    )[:10]

    complex_files = sorted(
        files,
        key=lambda x: x["complexity"],
        reverse=True,
    )[:10]

    risky_files = sorted(
        files,
        key=lambda x: x["risk"],
        reverse=True,
    )[:10]

    duplicate_files = sorted(
        files,
        key=lambda x: x["duplicate"],
        reverse=True,
    )[:10]

    dependency_cycles = list(
        nx.simple_cycles(graph)
    )

    architecture = architecture_score(
        summary,
        graph,
    )

    return {

        "overall_grade":
            summary["grade"],

        "code_health":
            summary["code_health"],

        "architecture_score":
            architecture,

        "risk_level":
            risk_level(summary["average_risk"]),

        "summary": summary,

        "top_hotspots": hotspots,

        "most_complex_files": complex_files,

        "highest_risk_files": risky_files,

        "duplicate_files": duplicate_files,

        "dependency_cycles": dependency_cycles,

        "git_statistics": git_stats,

        "recommendations":
            recommendations(
                summary,
                files,
                graph,
            ),
    }