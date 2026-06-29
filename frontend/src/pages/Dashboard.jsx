import { useEffect } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { analyzeRepository } from "../api/api";

import SummaryCard from "../components/SummaryCard";
import DataTable from "../components/DataTable";
import DependencyGraph from "../components/DependencyGraph";
import AIInsights from "../components/AIInsights";

export default function Dashboard() {
  const location = useLocation();

  const githubUrl = location.state?.githubUrl;

  if (!githubUrl) {
    return <Navigate to="/" replace />;
  }

  const {
    data,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["repository-analysis", githubUrl],
    queryFn: () => analyzeRepository(githubUrl),
    staleTime: Infinity,
  });

  useEffect(() => {
    document.title = "Repository Analysis";
  }, []);

  if (isLoading) {
    return (
        <div className="glass-card p-10 text-center">
            <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-[var(--border)] border-t-[var(--primary)]" />

            <h2 className="font-heading mt-6 text-3xl font-bold text-primary">
                Analyzing Repository...
            </h2>

            <p className="mt-3 text-neutral-400">
                Cloning repository, analyzing source files, generating engineering report and AI insights...
            </p>
        </div>
    );
  }

  if (isError) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-20">
        <div className="glass-card p-8">
          <h2 className="font-heading text-3xl font-bold text-red-400">
            Analysis Failed
          </h2>

          <p className="mt-4 text-neutral-300">
            {error?.message || "Something went wrong while analyzing the repository."}
          </p>
        </div>
      </div>
    );
  }

  const {
  summary,
  files,
  dependency_graph,
  git_statistics,
  readme,

  overall_grade,
  code_health,
  architecture_score,
  risk_level,

  top_hotspots,
  most_complex_files,
  highest_risk_files,
  duplicate_files,
  dependency_cycles,
  ai_insights,
  model,
  errorr,
} = data;
    return (
    <div className="mx-auto max-w-[1400px] px-6 py-0">
      <p className="text-center text-lg"> Curious how we analyze your repository? Explore the feature guide on the home page. </p>
      <h1 className="font-heading text-4xl font-bold">
        Repository Analysis
      </h1>

      <p className="mt-2 break-all text-neutral-400">
        {githubUrl}
      </p>

      <div className="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <SummaryCard
          title="Code Health"
          value={code_health}
        />

        <SummaryCard
          title="Architecture Score"
          value={architecture_score}
        />

        <SummaryCard
          title="Overall Grade"
          value={overall_grade}
        />

        <SummaryCard
          title="Risk Level"
          value={risk_level}
        />
      </div>

      <section className="glass-card mt-10 p-8">
        <h2 className="font-heading mb-6 text-2xl font-semibold">
          Git Statistics
        </h2>

        <div className="grid gap-8 md:grid-cols-3">
          <div>
            <p className="text-sm text-neutral-400">
              Total Commits
            </p>

            <p className="mt-2 text-3xl font-bold text-primary">
              {git_statistics.total_commits}
            </p>
          </div>

          <div>
            <p className="text-sm text-neutral-400">
              Contributors
            </p>

            <p className="mt-2 text-3xl font-bold text-primary">
              {Object.keys(git_statistics.contributors).length}
            </p>
          </div>

          <div>
            <p className="text-sm text-neutral-400">
              Default Branch
            </p>

            <p className="mt-2 text-3xl font-bold text-primary">
              {git_statistics.default_branch}
            </p>
          </div>
        </div>
      </section>

      <section className="mt-10">
        <DataTable files={files} />
      </section>

      <section className="glass-card mt-10 p-8">
        <h2 className="font-heading mb-6 text-2xl font-semibold">
          README Documentation
        </h2>

        {!readme.exists ? (
          <p className="text-red-400">
            No README.md file found.
          </p>
        ) : (
          <>
            <div className="mb-6">
              <p className="text-sm text-neutral-400">
                Documentation Score
              </p>

              <p className="mt-2 text-3xl font-bold text-primary">
                {readme.score}%
              </p>
            </div>

            {readme.missing_sections.length === 0 ? (
              <p className="text-green-400">
                ✓ All recommended documentation sections are present.
              </p>
            ) : (
              <>
                <p className="mb-3 font-medium">
                  Missing Sections
                </p>

                <ul className="space-y-2">
                  {readme.missing_sections.map((section) => (
                    <li key={section}>
                      • {section}
                    </li>
                  ))}
                </ul>
              </>
            )}
          </>
        )}
      </section>

      <section className="mt-10">
        <DependencyGraph
          graph={JSON.parse(dependency_graph)}
        />
      </section>

      <section className="glass-card mt-10 p-8">
        <h2 className="font-heading mb-6 text-2xl font-semibold">
          Top Hotspots
        </h2>

        <div className="space-y-3">
          {top_hotspots.slice(0, 5).map((file) => (
            <div
              key={file.file}
              className="flex items-center justify-between border-b border-[var(--border)] pb-2"
            >
              <span className="truncate">{file.file}</span>

              <span className="font-semibold text-primary">
                {file.hotspot}
              </span>
            </div>
          ))}
        </div>
      </section>

      <section className="glass-card mt-10 p-8">
        <h2 className="font-heading mb-6 text-2xl font-semibold">
          Highest Risk Files
        </h2>

        <div className="space-y-3">
          {highest_risk_files.slice(0, 5).map((file) => (
            <div
              key={file.file}
              className="flex items-center justify-between border-b border-[var(--border)] pb-2"
            >
              <span className="truncate">{file.file}</span>

              <span className="font-semibold text-red-400">
                {file.risk}
              </span>
            </div>
          ))}
        </div>
      </section>

      <section className="glass-card mt-10 p-8">
        <h2 className="font-heading mb-6 text-2xl font-semibold">
          Most Complex Files
        </h2>

        <div className="space-y-3">
          {most_complex_files.slice(0, 5).map((file) => (
            <div
              key={file.file}
              className="flex items-center justify-between border-b border-[var(--border)] pb-2"
            >
              <span className="truncate">{file.file}</span>

              <span className="font-semibold text-yellow-400">
                {file.complexity}
              </span>
            </div>
          ))}
        </div>
      </section>

      <section className="glass-card mt-10 p-8">
        <h2 className="font-heading mb-6 text-2xl font-semibold">
          Duplicate Files
        </h2>

        {duplicate_files.length === 0 ? (
          <p className="text-neutral-400">
            No significant duplicate code detected.
          </p>
        ) : (
          <div className="space-y-3">
            {duplicate_files.filter(file => file.duplicate > 5).slice(0, 5).map((file) => (
              <div
                key={file.file}
                className="flex items-center justify-between border-b border-[var(--border)] pb-2"
              >
                <span className="truncate">
                  {file.file}
                </span>

                <span className="font-semibold text-orange-400">
                  {file.duplicate.toFixed(2)}%
                </span>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="glass-card mt-10 p-8">
        <h2 className="font-heading mb-6 text-2xl font-semibold">
          Dependency Cycles
        </h2>

        {dependency_cycles.length === 0 ? (
          <p className="text-green-400">
            No circular dependencies detected.
          </p>
        ) : (
          <div className="space-y-4">
            {dependency_cycles.map((cycle, index) => (
              <div
                key={index}
                className="rounded-lg border border-[var(--border)] p-4"
              >
                {cycle.join(" → ")}
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="mt-10">
          <AIInsights insights={ai_insights} model={model} error={errorr}/>
      </section>

    </div>
  );
}