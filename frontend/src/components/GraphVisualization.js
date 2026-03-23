import React, { useRef, useEffect, useState, useMemo, useCallback } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';
import './GraphVisualization.css';

const GraphVisualization = ({ graphData, highlightedNodes, onNodeClick, selectedNode }) => {
  const graphRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [hoveredNode, setHoveredNode] = useState(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
  const hoverTimeoutRef = useRef(null);
  
  useEffect(() => {
    const updateDimensions = () => {
      const container = document.querySelector('.graph-container');
      if (container) {
        setDimensions({
          width: container.clientWidth,
          height: container.clientHeight,
        });
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    if (graphRef.current && highlightedNodes.length > 0) {
      // Zoom to highlighted nodes in 3D
      const node = graphData?.nodes.find(n => n.id === highlightedNodes[0]);
      if (node && node.x !== undefined && node.y !== undefined && node.z !== undefined) {
        const distance = 400;
        graphRef.current.cameraPosition(
          { x: node.x, y: node.y, z: node.z + distance },
          node,
          1500
        );
      }
    }
  }, [highlightedNodes, graphData]);

  // Configure camera and lighting controls
  useEffect(() => {
    if (graphRef.current) {
      const fg = graphRef.current;
      
      // Add ambient and directional lighting for better 3D visualization
      const scene = fg.scene();
      if (scene) {
        // Clear existing lights
        scene.children.filter(child => child.type === 'DirectionalLight' || child.type === 'AmbientLight')
          .forEach(light => scene.remove(light));
        
        // Add better lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        
        const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight1.position.set(200, 200, 200);
        scene.add(directionalLight1);
        
        const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
        directionalLight2.position.set(-200, -200, -200);
        scene.add(directionalLight2);
      }
      
      // Configure camera controls
      const controls = fg.controls();
      if (controls) {
        controls.enableDamping = true;
        controls.dampingFactor = 0.1;
        controls.rotateSpeed = 0.5;
        controls.zoomSpeed = 0.8;
        controls.minDistance = 100;
        controls.maxDistance = 2000;
      }
    }
  }, []);

  // Prepare graph data - memoized to prevent unnecessary recalculations
  const preparedData = useMemo(() => {
    if (!graphData) return { nodes: [], links: [] };
    
    return {
      nodes: graphData.nodes.map(node => ({
        ...node,
        val: getNodeSize(node.type),
        color: getNodeColor(node.type, highlightedNodes.includes(node.id), selectedNode?.id === node.id),
      })),
      links: graphData.edges.map(edge => ({
        source: edge.source,
        target: edge.target,
        label: edge.label || edge.type,
        color: highlightedNodes.includes(edge.source) || highlightedNodes.includes(edge.target) 
          ? '#ffeb3b' 
          : '#3949ab',
      })),
    };
  }, [graphData, highlightedNodes, selectedNode]);

  // Handle node hover with debouncing to reduce sensitivity
  const handleNodeHover = useCallback((node, prevNode) => {
    // Clear any existing timeout
    if (hoverTimeoutRef.current) {
      clearTimeout(hoverTimeoutRef.current);
    }

    if (node) {
      // Debounce hover activation by 150ms
      hoverTimeoutRef.current = setTimeout(() => {
        setHoveredNode(node);
      }, 150);
    } else {
      // Immediately clear on mouse leave
      setHoveredNode(null);
    }
  }, []);

  // Update tooltip position
  const handleMouseMove = useCallback((e) => {
    if (hoveredNode) {
      setTooltipPosition({
        x: e.clientX + 15,
        y: e.clientY + 15,
      });
    }
  }, [hoveredNode]);

  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [handleMouseMove]);

  const handleNodeClick = (node) => {
    if (onNodeClick) {
      onNodeClick(node);
    }
  };

  // Node 3D object customization
  const nodeThreeObject = useCallback((node) => {
    const geometry = new THREE.SphereGeometry(node.val || 5);
    const material = new THREE.MeshLambertMaterial({
      color: node.color,
      transparent: true,
      opacity: 0.9,
    });
    const mesh = new THREE.Mesh(geometry, material);
    
    // Add a ring for selected/highlighted nodes
    if (highlightedNodes.includes(node.id) || selectedNode?.id === node.id) {
      const ringGeometry = new THREE.RingGeometry(node.val * 1.5, node.val * 1.8, 32);
      const ringMaterial = new THREE.MeshBasicMaterial({
        color: selectedNode?.id === node.id ? '#ff1744' : '#ffeb3b',
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.8,
      });
      const ring = new THREE.Mesh(ringGeometry, ringMaterial);
      ring.lookAt(0, 0, 1);
      mesh.add(ring);
    }
    
    return mesh;
  }, [highlightedNodes, selectedNode]);

  // Link 3D object customization
  const linkThreeObject = useCallback((link) => {
    const isHighlighted = highlightedNodes.includes(link.source.id) || 
                         highlightedNodes.includes(link.target.id);
    
    if (isHighlighted) {
      // Create animated particles for highlighted links
      const material = new THREE.MeshBasicMaterial({ 
        color: '#ffeb3b',
        transparent: true,
        opacity: 0.8,
      });
      const geometry = new THREE.CylinderGeometry(0.5, 0.5, 1, 6);
      return new THREE.Mesh(geometry, material);
    }
    return null;
  }, [highlightedNodes]);

  if (!graphData) {
    return <div className="graph-loading">Loading graph...</div>;
  }

  return (
    <div className="graph-container">
      <div className="graph-controls">
        <button 
          className="control-btn"
          onClick={() => {
            if (graphRef.current) {
              graphRef.current.zoomToFit(400);
            }
          }}
        >
          Fit View
        </button>
        <button 
          className="control-btn"
          onClick={() => {
            if (graphRef.current) {
              graphRef.current.cameraPosition(
                { x: 0, y: 0, z: 1000 },
                { x: 0, y: 0, z: 0 },
                1000
              );
            }
          }}
        >
          Reset View
        </button>
        <button 
          className="control-btn"
          onClick={() => {
            if (graphRef.current) {
              graphRef.current.cameraPosition(
                { x: 800, y: 800, z: 800 },
                { x: 0, y: 0, z: 0 },
                1000
              );
            }
          }}
        >
          Isometric
        </button>
      </div>
      
      <ForceGraph3D
        ref={graphRef}
        width={dimensions.width}
        height={dimensions.height}
        graphData={preparedData}
        nodeThreeObject={nodeThreeObject}
        nodeLabel={() => ''} // Disable default tooltip
        linkThreeObject={linkThreeObject}
        linkThreeObjectExtend={true}
        linkColor={link => link.color}
        linkWidth={link => highlightedNodes.includes(link.source.id) || highlightedNodes.includes(link.target.id) ? 2 : 0.5}
        linkDirectionalArrowLength={3}
        linkDirectionalArrowRelPos={1}
        linkDirectionalParticles={link => highlightedNodes.includes(link.source.id) || highlightedNodes.includes(link.target.id) ? 4 : 0}
        linkDirectionalParticleWidth={2}
        linkDirectionalParticleSpeed={0.006}
        onNodeClick={handleNodeClick}
        onNodeHover={handleNodeHover}
        enableNodeDrag={true}
        enableNavigationControls={true}
        showNavInfo={false}
        cooldownTime={2000}
        d3AlphaDecay={0.01}
        d3VelocityDecay={0.3}
        d3Force={{
          charge: { strength: -200 },
          link: { distance: 100 }
        }}
        backgroundColor="rgba(10, 14, 39, 0)"
      />
      
      {/* Custom Tooltip */}
      {hoveredNode && (
        <div 
          className="node-tooltip"
          style={{
            left: `${tooltipPosition.x}px`,
            top: `${tooltipPosition.y}px`,
          }}
        >
          <div className="tooltip-header">{hoveredNode.label}</div>
          <div className="tooltip-type">Type: {hoveredNode.type}</div>
          {hoveredNode.id && <div className="tooltip-id">ID: {hoveredNode.id}</div>}
          {hoveredNode.properties && Object.keys(hoveredNode.properties).length > 0 && (
            <div className="tooltip-properties">
              {Object.entries(hoveredNode.properties).slice(0, 3).map(([key, value]) => (
                <div key={key} className="tooltip-prop">
                  <span className="prop-key">{key}:</span>
                  <span className="prop-value">{String(value).substring(0, 30)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      <div className="graph-info">
        <div className="info-item">
          <span className="info-label">Nodes:</span>
          <span className="info-value">{preparedData.nodes.length}</span>
        </div>
        <div className="info-item">
          <span className="info-label">Links:</span>
          <span className="info-value">{preparedData.links.length}</span>
        </div>
      </div>
      
      <div className="graph-legend">
        <div className="legend-title">Node Types</div>
        {Object.entries(NODE_TYPE_COLORS).map(([type, color]) => (
          <div key={type} className="legend-item">
            <div className="legend-color" style={{ background: color }}></div>
            <span>{type}</span>
          </div>
        ))}
      </div>
      
      <div className="graph-instructions">
        <div className="instruction-title">Controls</div>
        <div className="instruction-item">🖱️ Left click + drag: Rotate</div>
        <div className="instruction-item">🖱️ Right click + drag: Pan</div>
        <div className="instruction-item">🖱️ Scroll: Zoom</div>
        <div className="instruction-item">👆 Click node: View details</div>
      </div>
    </div>
  );
};

// Helper functions
const NODE_TYPE_COLORS = {
  Customer: '#e91e63',
  SalesOrder: '#2196f3',
  SalesOrderItem: '#64b5f6',
  Delivery: '#ff9800',
  DeliveryItem: '#ffb74d',
  Invoice: '#4caf50',
  InvoiceItem: '#81c784',
  JournalEntry: '#9c27b0',
  Payment: '#00bcd4',
  Product: '#ffeb3b',
  Plant: '#795548',
  Address: '#607d8b',
};

const getNodeColor = (type, isHighlighted, isSelected) => {
  if (isSelected) return '#ff1744';
  if (isHighlighted) return '#ffeb3b';
  return NODE_TYPE_COLORS[type] || '#9e9e9e';
};

const getNodeSize = (type) => {
  const sizes = {
    Customer: 12,
    SalesOrder: 10,
    SalesOrderItem: 5,
    Delivery: 8,
    DeliveryItem: 5,
    Invoice: 10,
    InvoiceItem: 5,
    JournalEntry: 8,
    Payment: 8,
    Product: 6,
    Plant: 6,
    Address: 4,
  };
  return sizes[type] || 6;
};

export default GraphVisualization;
