import { useMemo } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
} from "reactflow";
import "reactflow/dist/style.css";

export default function DependencyGraph({ graph }) {
  const { nodes, edges } = useMemo(() => {
    const nodes = graph.nodes.map((node, index) => {
      const normalizedId = node.id.replace(/\\/g, "/");
      
      return {
        id: normalizedId, // Set clean matching ID
        data: {
          label: normalizedId.split("/").pop(), 
        },
        position: {
          x: (index % 5) * 250,
          y: Math.floor(index / 5) * 120,
        },
      };
    });

    const edges = graph.links.map((edge, index) => ({
      id: `${edge.source}-${edge.target}-${index}`,
      source: edge.source.replace(/\\/g, "/"),
      target: edge.target.replace(/\\/g, "/"),
      animated: true,
    }));

    return { nodes, edges };
  }, [graph]);

  return (
    <div className="glass-card dependency-card">
      <div className="dependency-header">
        <h2 className="dependency-title font-heading text-2x1 font-semibold">
          Dependency Graph
        </h2>
      </div>

      <div className="dependency-graph">
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