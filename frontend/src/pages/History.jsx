export default function History() {
  return (
    <div className="mx-auto max-w-[1400px] px-6 py-10">
      <h1 className="font-heading text-4xl font-bold">
        Analysis History
      </h1>

      <p className="mt-2 text-neutral-400">
        Previously analyzed repositories will appear here.
      </p>

      <div className="glass-card mt-10 flex h-72 items-center justify-center">
        <div className="text-center">
          <h2 className="font-heading text-2xl font-semibold">
            No History Yet
          </h2>

          <p className="mt-3 text-neutral-400">
            Analyze your first GitHub repository to populate this page.
          </p>
        </div>
      </div>
    </div>
  );
}