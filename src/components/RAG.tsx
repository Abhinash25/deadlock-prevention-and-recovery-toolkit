import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface Node extends d3.SimulationNodeDatum {
  id: string;
  type: 'process' | 'resource';
}

interface Edge extends d3.SimulationLinkDatum<Node> {
  source: string;
  target: string;
}

interface RAGProps {
  nodes: Node[];
  edges: Edge[];
  highlightPath?: string[];
}

const RAG: React.FC<RAGProps> = ({ nodes, edges, highlightPath = [] }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const width = 800;
    const height = 500;
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Deep clone to prevent D3 from mutating React state
    const simNodes: Node[] = nodes.map(n => ({ ...n }));
    const simEdges: Edge[] = edges.map(e => ({
      source: typeof e.source === 'string' ? e.source : (e.source as any).id,
      target: typeof e.target === 'string' ? e.target : (e.target as any).id,
    }));

    const simulation = d3.forceSimulation<Node>(simNodes)
      .force("link", d3.forceLink<Node, Edge>(simEdges).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    // Arrowhead definition
    svg.append("defs").append("marker")
      .attr("id", "arrowhead")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 25)
      .attr("refY", 0)
      .attr("orient", "auto")
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("xoverflow", "visible")
      .append("svg:path")
      .attr("d", "M 0,-5 L 10 ,0 L 0,5")
      .attr("fill", "#a8a29e")
      .style("stroke", "none");

    const link = svg.append("g")
      .attr("stroke", "#a8a29e")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(simEdges)
      .join("line")
      .attr("stroke-width", 2)
      .attr("marker-end", "url(#arrowhead)")
      .attr("stroke", (d: any) => {
        const s = typeof d.source === 'string' ? d.source : (d.source as Node).id;
        const t = typeof d.target === 'string' ? d.target : (d.target as Node).id;
        if (highlightPath.includes(s) && highlightPath.includes(t)) {
          const sIdx = highlightPath.indexOf(s);
          const tIdx = highlightPath.indexOf(t);
          // Check if they are consecutive in the cycle
          if (Math.abs(sIdx - tIdx) === 1 || (sIdx === 0 && tIdx === highlightPath.length - 1) || (tIdx === 0 && sIdx === highlightPath.length - 1)) {
            return "#ef4444";
          }
        }
        return "#a8a29e";
      });

    const node = svg.append("g")
      .selectAll("g")
      .data(simNodes)
      .join("g")
      .call(d3.drag<SVGGElement, Node>()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended) as any);

    node.append("circle")
      .attr("r", 20)
      .attr("fill", (d: any) => d.type === 'process' ? "#3b82f6" : "#10b981")
      .attr("stroke", (d: any) => highlightPath.includes(d.id) ? "#ef4444" : "#e7e5e4")
      .attr("stroke-width", (d: any) => highlightPath.includes(d.id) ? 3 : 2);

    node.append("text")
      .text((d: any) => d.id)
      .attr("x", 0)
      .attr("y", 5)
      .attr("text-anchor", "middle")
      .attr("fill", "white")
      .attr("font-size", "12px")
      .attr("font-weight", "bold");

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => (d.source as any).x)
        .attr("y1", (d: any) => (d.source as any).y)
        .attr("x2", (d: any) => (d.target as any).x)
        .attr("y2", (d: any) => (d.target as any).y);

      node
        .attr("transform", (d: any) => `translate(${(d as any).x},${(d as any).y})`);
    });

    function dragstarted(event: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event: any) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event: any) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    return () => simulation.stop();
  }, [nodes, edges, highlightPath]);

  return (
    <div className="w-full h-[500px] bg-stone-50 rounded-xl border border-stone-200 overflow-hidden">
      <svg ref={svgRef} width="100%" height="100%" viewBox="0 0 800 500" />
    </div>
  );
};

export default RAG;
