export default function DataTable({ files }) {
  return (
    <div className="glass-card overflow-hidden">
      <div className="border-b border-theme p-6">
        <h2 className="font-heading text-2xl font-semibold">
          File Metrics
        </h2>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-left">
          <thead className="border-b border-theme text-sm text-neutral-400">
            <tr>
              <th className="px-6 py-4">File</th>
              <th className="px-6 py-4">Language</th>
              <th className="px-6 py-4">Lines</th>
              <th className="px-6 py-4">Complexity</th>
              <th className="px-6 py-4">Maintainability</th>
              <th className="px-6 py-4">Risk</th>
              <th className="px-6 py-4">Duplicate %</th>
              <th className="px-6 py-4">Hotspot</th>
            </tr>
          </thead>

          <tbody>
            {files.map((file, index) => (
              <tr
                key={index}
                className="border-b border-theme/40 hover:bg-white/5"
              >
                <td className="max-w-sm truncate px-6 py-4">
                  {file.file}
                </td>

                <td className="px-6 py-4">
                  {file.language}
                </td>

                <td className="px-6 py-4">
                  {file.lines}
                </td>

                <td className="px-6 py-4">
                  {file.complexity}
                </td>

                <td className="px-6 py-4">
                  {file.maintainability}
                </td>

                <td className="px-6 py-4">
                  {file.risk}
                </td>

                <td className="px-6 py-4">
                  {file.duplicate}%
                </td>

                <td className="px-6 py-4">
                  {file.hotspot}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}