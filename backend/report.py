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
    if graph is None or len(graph.nodes) == 0:
        return summary["code_health"]

    base_score = summary["code_health"]
    
    try:
        cycles = len(list(nx.simple_cycles(graph)))
        cycle_penalty = min(cycles * 3, 20)
    except Exception:
        cycle_penalty = 0

    coupling_penalty = 0
    total_nodes = len(graph.nodes)
    
    for node in graph.nodes:
        fan_in = graph.in_degree(node)
        fan_out = graph.out_degree(node)
        
        if total_nodes > 3 and fan_out > (total_nodes * 0.30):
            coupling_penalty += 2
            
        if total_nodes > 3 and fan_in > (total_nodes * 0.50):
            coupling_penalty += 1

    coupling_penalty = min(coupling_penalty, 15)

    density = nx.density(graph)
    density_penalty = min(density * 40, 15)  # Max 15 point penalty for pure spaghetti

    final_score = base_score - (cycle_penalty + coupling_penalty + density_penalty)

    return round(max(0, min(100, final_score)), 2)

def generate_report(summary, files, graph, git_stats, readme):

    hotspots = sorted(
        files,
        key=lambda x: x["hotspot"],
        reverse=True,
    )[:5]

    complex_files = sorted(
        files,
        key=lambda x: x["complexity"],
        reverse=True,
    )[:5]

    risky_files = sorted(
        files,
        key=lambda x: x["risk"],
        reverse=True,
    )[:5]

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
        "readme": readme,
        "top_hotspots": hotspots,
        "most_complex_files": complex_files,
        "highest_risk_files": risky_files,
        "duplicate_files": duplicate_files,
        "dependency_cycles": dependency_cycles,
    }