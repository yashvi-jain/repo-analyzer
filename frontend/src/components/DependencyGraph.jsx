import { useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
} from "reactflow";
import "reactflow/dist/style.css";

export default function DependencyGraph({ graph }) {
  const { nodes, edges } = useMemo(() => {
    const nodes = graph.nodes.map((node, index) => ({
      id: node.id,
      data: {
        label: node.id.split("/").pop(),
      },
      position: {
        x: (index % 5) * 250,
        y: Math.floor(index / 5) * 120,
      },
    }));

    const edges = graph.links.map((edge, index) => ({
      id: `${edge.source}-${edge.target}-${index}`,
      source: edge.source,
      target: edge.target,
      animated: true,
    }));

    return { nodes, edges };
  }, [graph]);

  return (
    <div className="glass-card">
      <div className="border-b border-theme p-6">
        <h2 className="font-heading text-2xl font-semibold">
          Dependency Graph
        </h2>
      </div>

      <div className="h-[700px]">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
        >
          <MiniMap />
          <Controls />
          <Background />
        </ReactFlow>
      </div>
    </div>
  );
}