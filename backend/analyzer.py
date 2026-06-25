from github_utils import (
    clone_repository,
    get_all_source_files,
    build_dependency_graph,
    dependency_graph_json,
    get_git_statistics,
    analyze_readme,
)
from metrics import analyze_repository
from report import generate_report
from ai_insights import generate_ai_insights
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Repository, Analysis, FileMetric
import traceback

def save_analysis(
    github_url: str,
    repo_path: str,
    analysis_result: dict,
    report: dict,
):
    """
    Persist analysis to PostgreSQL.
    """

    db: Session = SessionLocal()

    try:

        repository = db.query(Repository).filter(
            Repository.github_url == github_url
        ).first()

        if repository is None:

            repository = Repository(
                github_url=github_url,
                name=github_url.rstrip("/").split("/")[-1],
                local_path=repo_path,
            )

            db.add(repository)
            db.commit()
            db.refresh(repository)

        analysis = Analysis(
            repository_id=repository.id,
            overall_risk=analysis_result["summary"]["average_risk"],
            average_complexity=analysis_result["summary"]["average_complexity"],
            maintainability_index=analysis_result["summary"]["average_maintainability"],
            architecture_score=report["architecture_score"],
            code_health=report["code_health"],
            overall_grade=report["overall_grade"],
            risk_level=report["risk_level"],
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        for file in analysis_result["files"]:

            metric = FileMetric(
                analysis_id=analysis.id,
                file_path=file["file"],
                language=file["language"],
                lines=file["lines"],
                cyclomatic_complexity=file["complexity"],
                maintainability_index=file["maintainability"],
                risk_score=file["risk"],
                duplicate_percentage=file["duplicate"],
                hotspot_score=file["hotspot"],
                git_churn=file["git_churn"],
                dead_code=str(file["dead_code"]),
            )

            db.add(metric)

        db.commit()

    finally:

        db.close()

def analyze_github_repository(github_url: str):
    """
    Complete repository analysis pipeline.
    """

    # Clone repository
    repo_path = clone_repository(github_url)

    # Discover source files
    source_files = get_all_source_files(repo_path)

    # Build dependency graph
    graph = build_dependency_graph(repo_path, source_files)

    # Static analysis
    analysis = analyze_repository(
        repo_path,
        source_files,
        graph,
    )

    # Git analytics
    git_stats = get_git_statistics(repo_path)

    # README analysis
    readme = analyze_readme(repo_path)

    # Final report
    report = generate_report(
        analysis["summary"],
        analysis["files"],
        graph,
        git_stats,
        readme,
    )

    important = {}

    for file in report["highest_risk_files"]:
        important[file["file"]] = file

    for file in report["most_complex_files"]:
        important[file["file"]] = file

    for file in report["top_hotspots"]:
        important[file["file"]] = file

    for file in report["duplicate_files"]:
        important[file["file"]] = file

    try:
        ai_insights = generate_ai_insights(
            repo_path,
            list(important.values())
        )
    except Exception as e:
        traceback.print_exc()
        ai_insights = {
            "error": str(e)
        }

    save_analysis(
        github_url,
        repo_path,
        analysis,
        report,
    )

    return {
        "repository": github_url,
        "summary": analysis["summary"],
        "files": analysis["files"],
        "dependency_graph": dependency_graph_json(graph),
        "git_statistics": git_stats,
        "overall_grade": report["overall_grade"],
        "code_health": report["code_health"],
        "architecture_score": report["architecture_score"],
        "risk_level": report["risk_level"],
        "readme": report["readme"],
        "top_hotspots": report["top_hotspots"],
        "most_complex_files": report["most_complex_files"],
        "highest_risk_files": report["highest_risk_files"],
        "duplicate_files": report["duplicate_files"],
        "dependency_cycles": report["dependency_cycles"],
        "ai_insights": ai_insights,
    }