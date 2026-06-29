import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Clipboard,
  Activity,
  ShieldAlert,
  Network,
  BarChart3,
  GitBranch,
  Files,
  Wrench,
  GitCommitHorizontal,
  Sparkles,
  Flame,
  Copy,
} from "lucide-react";
import { FaGithub } from "react-icons/fa";

const features = [
  {
    title: "AI Insights",
    description:
      "Uses Gemini 2.5 Flash with automatic Groq fallback to explain engineering issues, identify root causes behind high-risk metrics, and suggest practical refactoring strategies for important files.",
    icon: Sparkles,
  },
  {
    title: "Code Health",
    description:
      "An overall quality score computed from maintainability, complexity, engineering risk, duplication, architecture, and code quality metrics. Higher is better.",
    icon: Activity,
  },
  {
    title: "Architecture Score",
    description:
      "Evaluates the overall project structure based on dependency cycles, modularity, coupling, and overall code health. Higher is better.",
    icon: Network,
  },
  {
    title: "Engineering Risk",
    description:
      "A composite score calculated from complexity, maintainability, Git churn, hotspots, duplication, and potential dead code to identify files most likely to cause future issues. Lower is better.",
    icon: ShieldAlert,
  },
  {
    title: "Complexity Analysis",
    description:
      "Measures the number of logical execution paths through your code. Higher complexity means harder testing, debugging, and maintenance. Lower is better.",
    icon: BarChart3,
  },
  {
    title: "Maintainability Index",
    description:
      "Estimates how easy the codebase is to maintain using Halstead Volume, cyclomatic complexity, and lines of code. Higher is better.",
    icon: Wrench,
  },
  {
    title: "Dependency Analysis",
    description:
      "Builds a complete dependency graph using AST parsing (Python) and include parsing (C/C++) to visualize module relationships and detect circular dependencies.",
    icon: GitBranch,
  },
  {
    title: "Top Hotspots",
    description:
      "Identifies files with the highest maintenance burden by combining cyclomatic complexity and Git churn. These files are often the best candidates for refactoring.",
    icon: Flame,
  },
  {
    title: "Git Analytics",
    description:
      "Analyzes commit history, file churn, contributor activity, and modification frequency to understand how the repository evolves over time.",
    icon: GitCommitHorizontal,
  },
  {
    title: "Duplicate Detection",
    description:
      "Detects structurally similar code using fingerprint-based similarity analysis, helping reduce maintenance effort and inconsistent bug fixes. Lower is better.",
    icon: Copy,
  },
];

export default function Home() {
  const navigate = useNavigate();

  const [githubUrl, setGithubUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const isValidGithubUrl = (url) =>
    /^https:\/\/github\.com\/[^/]+\/[^/]+\/?$/.test(url.trim());

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setGithubUrl(text);
    } catch {
      // ignore clipboard errors
    }
  };

  const handleAnalyze = () => {
    if (!isValidGithubUrl(githubUrl) || loading) return;

    setLoading(true);

    navigate("/dashboard", {
      state: {
        githubUrl: githubUrl.trim(),
      },
    });
  };

  return (
    <div className="mx-auto max-w-[1400px] px-6 py-0">
      <section className="flex flex-col items-center text-center">

        {/* <div className="glass-card mb-8 inline-flex items-center gap-2 px-4 py-2">
          <FaGithub size={18} />
          <span className="text-sm text-neutral-300">
            GitHub Repository Analyzer
          </span>
        </div> */}

        <h1 className="font-heading text-4xl font-bold leading-tight md:text-6xl">
          Understand Any
          <span className="text-primary block">
            GitHub Repository
          </span>
        </h1>

        <p className="mt-6 max-w-3xl text-lg leading-8 text-neutral-400">
          Upload a public GitHub repository and receive detailed insights into
          architecture, code quality, complexity, dependency structure,
          engineering risks, and repository health.
        </p>

        <div className="mt-12 w-full max-w-3xl">
          <div className="glass-card flex overflow-hidden">

            <div className="flex items-center px-5 text-neutral-400">
              <FaGithub size={22} />
            </div>

            <input
              type="text"
              placeholder="https://github.com/owner/repository"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleAnalyze();
              }}
              className="flex-1 bg-transparent px-2 py-5 placeholder:text-neutral-500"
            />

            <button
              onClick={handlePaste}
              className="border-theme flex items-center gap-2 border-l px-5 transition hover:bg-white/10"
            >
              <Clipboard size={18} />
              <span className="hidden sm:inline">
                Paste
              </span>
            </button>

          </div>

          {!isValidGithubUrl(githubUrl) && githubUrl.length > 0 && (
            <p className="mt-3 text-left text-sm text-red-400">
              Enter a valid GitHub repository URL.
            </p>
          )}

          <button
            onClick={handleAnalyze}
            disabled={!isValidGithubUrl(githubUrl) || loading}
            className="bg-primary mt-5 w-full rounded-[var(--radius)] py-4 font-semibold text-[#1A1F1A] transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Analyzing..." : "Analyze Repository"}
          </button>

          <p className="mt-5 text-sm text-neutral-400">
            Supports Python, C, C++, JavaScript and TypeScript repositories
          </p>
        </div>
      </section>
      <p className="text-center p-6 text-lg"> Curious how we analyze your repository? Explore the feature guide below before moving forward. </p>
      <section className="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {features.map((feature) => {
          const Icon = feature.icon;

          return (
            <div
              key={feature.title}
              className="glass-card group p-7 transition-all duration-300 hover:-translate-y-1 hover:border-[var(--primary)]"
            >
              <div
                className="
                  mb-5
                  flex
                  h-14
                  w-14
                  items-center
                  justify-center
                  rounded-2xl
                  bg-[#7b9669]/15
                  text-[#7b9669]
                  transition
                  group-hover:scale-105
                "
              >
                <Icon size={28} strokeWidth={2} />
              </div>

              <h3 className="font-heading text-xl font-semibold">
                {feature.title}
              </h3>

              <p className="mt-3 leading-7 text-neutral-400">
                {feature.description}
              </p>
            </div>
          );
        })}
      </section>
    </div>
  );
}