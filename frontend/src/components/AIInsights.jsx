export default function AIInsights({ insights, model, error}) {
  if (!insights) return null;

  if (error) {
    return (
      <section className="glass-card p-8">
        <h2 className="font-heading text-2xl font-semibold">
            AI Engineering Insights
        </h2>

        <p className="mt-4 text-red-400">
            Failed to generate AI insights.
        </p>
      </section>
    );
  }

  return (
    <section className="glass-card p-8">

      <h2 className="font-heading mb-6 text-2xl font-semibold">
        AI Engineering Insights
      </h2>
      <div className="font-semibold">{model==="gemini"? "Current model - Gemini 2.5 Flash" : "Gemini server busy. Used fallback model."}</div>
      <div className="space-y-8">

        {insights.map((item) => {

          const causes = item.root_causes ?? [];
          const suggestions = item.suggestions ?? [];

          const severityColor =
            item.severity === "high"
              ? "text-red-400"
              : item.severity === "medium"
              ? "text-yellow-400"
              : "text-green-400";

          return (

            <div
              key={item.file}
              className="rounded-xl border border-[var(--border)] p-6"
            >

              <div className="flex items-center justify-between gap-4">

                <h3 className="font-mono text-lg font-semibold text-primary break-all">
                  {item.file}
                </h3>

                <span className={`font-semibold uppercase ${severityColor}`}>
                  {item.severity}
                </span>

              </div>

              <p className="mt-5 text-neutral-300">
                {item.summary}
              </p>

              <div className="mt-6">

                <h4 className="font-semibold">
                  Root Causes
                </h4>

                <ul className="mt-2 space-y-2">

                  {causes.map((cause) => (

                    <li key={cause}>
                      • {cause}
                    </li>

                  ))}

                </ul>

              </div>

              <div className="mt-6">

                <h4 className="font-semibold text-green-400">
                  Suggestions
                </h4>

                <ul className="mt-2 space-y-2">

                  {suggestions.map((suggestion) => (

                    <li key={suggestion}>
                      ✓ {suggestion}
                    </li>

                  ))}

                </ul>

              </div>

            </div>

          );
        })}

      </div>

    </section>
  );
}