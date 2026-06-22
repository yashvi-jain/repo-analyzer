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
} from "lucide-react";
import { FaGithub } from "react-icons/fa";

const features = [
  {
    title: "Code Health",
    description:
      "Evaluate maintainability, documentation, and overall repository quality.",
    icon: Activity,
  },
  {
    title: "Complexity Analysis",
    description:
      "Measure cyclomatic complexity and identify difficult-to-maintain files.",
    icon: BarChart3,
  },
  {
    title: "Engineering Risk",
    description:
      "Detect risky modules, technical debt, and potential bottlenecks.",
    icon: ShieldAlert,
  },
  {
    title: "Architecture Score",
    description:
      "Analyze project organization and architectural consistency.",
    icon: Network,
  },
  {
    title: "Dependency Analysis",
    description:
      "Visualize relationships between files and modules.",
    icon: GitBranch,
  },
  {
    title: "Hotspots & Duplicates",
    description:
      "Find duplicate code and frequently changing files.",
    icon: Files,
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
    <div className="mx-auto max-w-[1400px] px-6 py-14">
      <section className="flex flex-col items-center text-center">

        <div className="glass-card mb-8 inline-flex items-center gap-2 px-4 py-2">
          <FaGithub size={18} />
          <span className="text-sm text-neutral-300">
            Repository Analysis
          </span>
        </div>

        <h1 className="font-heading text-5xl font-bold leading-tight md:text-6xl">
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
            <section className="mt-20 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
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