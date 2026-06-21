export default function SummaryCard({ title, value }) {
  return (
    <div className="glass-card transition-all duration-300 hover:-translate-y-1 hover:border-[var(--primary)]">
      <div className="p-6">
        <p className="text-sm text-neutral-400">
          {title}
        </p>

        <h3 className="font-heading mt-3 text-3xl font-bold text-primary">
          {value}
        </h3>
      </div>
    </div>
  );
}