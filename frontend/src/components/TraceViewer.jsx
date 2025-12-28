import React, { useState, useEffect } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

function TraceViewer({ traceId }) {
    const [trace, setTrace] = useState(null);
    const [selectedStep, setSelectedStep] = useState(null);
    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);

    const getNodeStyle = (status, nodeColor, isSelected) => {
        return {
            background: `linear-gradient(135deg, ${nodeColor}15 0%, ${nodeColor}08 100%)`,
            borderRadius: '8px',
            border: `1.5px solid ${isSelected ? '#818cf8' : `${nodeColor}40`}`,
            padding: '10px 12px',
            minWidth: '140px',
            maxWidth: '180px',
            color: '#e5e7eb',
            cursor: 'grab',
            fontSize: '11px',
            fontWeight: 500,
            boxShadow: isSelected
                ? '0 4px 12px rgba(129, 140, 248, 0.2)'
                : '0 2px 8px rgba(0, 0, 0, 0.3)',
        };
    };

    const updateFlow = (steps) => {
        const newNodes = [];
        const newEdges = [];

        steps.forEach((step, index) => {
            const status = step.status || 'success';
            let nodeColor = '#10b981';
            if (status === 'error') nodeColor = '#ef4444';
            else if (status === 'warning') nodeColor = '#f59e0b';
            else if (status === 'partial') nodeColor = '#3b82f6';

            newNodes.push({
                id: `step-${index}`,
                position: { x: 250, y: index * 100 + 50 },
                data: {
                    label: (
                        <div className="text-center max-w-full break-words">
                            <div className="font-semibold text-[11px] leading-tight text-gray-100 mb-1">
                                {step.name}
                            </div>
                            <div className="text-[9px] text-gray-400 bg-[#1f1f1f] rounded px-2 py-0.5 inline-block">
                                {step.step_type}
                            </div>
                        </div>
                    ),
                },
                style: getNodeStyle(status, nodeColor, selectedStep === index),
                draggable: true,
            });

            if (index > 0) {
                newEdges.push({
                    id: `edge-${index}`,
                    source: `step-${index - 1}`,
                    target: `step-${index}`,
                    type: 'smoothstep',
                    style: { stroke: `${nodeColor}60`, strokeWidth: 2 },
                    markerEnd: {
                        type: MarkerType.ArrowClosed,
                        width: 18,
                        height: 18,
                        color: `${nodeColor}60`,
                    },
                });
            }
        });

        setNodes(newNodes);
        setEdges(newEdges);
    };

    const fetchTrace = async () => {
        try {
            const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/api/traces/${traceId}`);
            const data = await res.json();
            setTrace(data);
            updateFlow(data.steps || []);
        } catch (error) {
            console.error('Failed to fetch trace:', error);
        }
    };

    useEffect(() => {
        fetchTrace();
    }, [traceId]);

    useEffect(() => {
        if (trace && trace.steps) {
            updateFlow(trace.steps);
        }
    }, [selectedStep]);

    const getStatusBadge = (status) => {
        const colors = {
            success: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
            error: 'bg-red-500/20 text-red-400 border-red-500/30',
            warning: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
            partial: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
        };
        return (
            <span className={`px-2 py-0.5 rounded-md text-[10px] font-medium border ${colors[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30'}`}>
                {status}
            </span>
        );
    };

    if (!trace) {
        return (
            <div className="flex items-center justify-center h-full bg-[#0a0a0a] text-gray-500">
                <div className="text-center">
                    <div className="w-12 h-12 bg-[#1f1f1f] rounded-lg flex items-center justify-center mx-auto mb-3 animate-pulse">
                        <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                    </div>
                    <p className="text-sm">Loading trace...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex h-full bg-[#0a0a0a]">
            {/* Flow Canvas */}
            <div className="flex-1 relative">
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    nodesDraggable
                    nodesConnectable={false}
                    onNodeClick={(event, node) => {
                        const stepIndex = parseInt(node.id.split('-')[1]);
                        setSelectedStep(stepIndex);
                    }}
                    fitView
                    fitViewOptions={{ padding: 0.2 }}
                >
                    <Background variant="dots" gap={16} size={1} color="#1f1f1f" />
                    <Controls className="bg-[#111111] border border-[#1f1f1f] rounded-lg shadow-lg" />
                    <MiniMap
                        className="bg-[#111111] border border-[#1f1f1f] rounded-lg shadow-lg"
                        nodeSize={8}
                        pannable={false}
                        zoomable={false}
                    />
                </ReactFlow>
            </div>

            {/* Right Sidebar - Langfuse style */}
            <div className="w-96 bg-[#111111] border-l border-[#1f1f1f] overflow-y-auto">
                <div className="p-6 space-y-6">
                    {/* Header */}
                    <div>
                        <h2 className="text-lg font-semibold text-gray-100 mb-2 break-words">
                            {trace.name}
                        </h2>
                        <div className="flex items-center gap-2 mb-4">
                            {getStatusBadge(trace.status)}
                        </div>
                    </div>

                    {/* Trace Info */}
                    <div className="space-y-3">
                        <div className="p-3 bg-[#0f0f0f] rounded-lg border border-[#1f1f1f]">
                            <div className="text-xs text-gray-500 mb-1">Trace ID</div>
                            <code className="text-xs text-gray-300 font-mono break-all">{trace.trace_id}</code>
                        </div>
                        <div className="p-3 bg-[#0f0f0f] rounded-lg border border-[#1f1f1f]">
                            <div className="text-xs text-gray-500 mb-1">Created</div>
                            <div className="text-sm text-gray-300">
                                {new Date(trace.created_at).toLocaleString()}
                            </div>
                        </div>
                        {trace.metadata && Object.keys(trace.metadata).length > 0 && (
                            <div className="p-3 bg-[#0f0f0f] rounded-lg border border-[#1f1f1f]">
                                <div className="text-xs text-gray-500 mb-2">Metadata</div>
                                <div className="space-y-1">
                                    {Object.entries(trace.metadata).map(([key, value]) => (
                                        <div key={key} className="text-xs">
                                            <span className="text-gray-500">{key}:</span>{' '}
                                            <span className="text-gray-300">{String(value)}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Steps List */}
                    <div>
                        <h3 className="text-sm font-semibold text-gray-200 mb-3">Steps</h3>
                        <div className="space-y-2">
                            {trace.steps && trace.steps.length > 0 ? (
                                trace.steps.map((step, index) => (
                                    <div
                                        key={index}
                                        onClick={() => setSelectedStep(index)}
                                        className={`p-3 rounded-lg border cursor-pointer transition-all ${selectedStep === index
                                            ? 'bg-indigo-500/10 border-indigo-500/50'
                                            : 'bg-[#0f0f0f] border-[#1f1f1f] hover:bg-[#151515] hover:border-[#2a2a2a]'
                                            }`}
                                    >
                                        <div className="flex items-start justify-between gap-2 mb-1">
                                            <div className="flex-1">
                                                <div className="text-sm font-medium text-gray-200 break-words">
                                                    {step.name}
                                                </div>
                                                <div className="text-xs text-gray-500 mt-0.5">
                                                    {step.step_type}
                                                </div>
                                            </div>
                                            {getStatusBadge(step.status)}
                                        </div>
                                        {step.reasoning && (
                                            <p className="text-xs text-gray-400 mt-2 line-clamp-2 break-words">
                                                {step.reasoning}
                                            </p>
                                        )}
                                    </div>
                                ))
                            ) : (
                                <div className="text-sm text-gray-500 text-center py-4">
                                    No steps available
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Step Details */}
                    {selectedStep !== null && trace.steps && trace.steps[selectedStep] && (
                        <div className="border-t border-[#1f1f1f] pt-6 space-y-4">
                            <h3 className="text-sm font-semibold text-gray-200">Step Details</h3>

                            {trace.steps[selectedStep].input && (
                                <div>
                                    <div className="text-xs text-gray-500 mb-2 font-medium">Input</div>
                                    <pre className="bg-[#0a0a0a] border border-[#1f1f1f] p-3 rounded-lg text-xs overflow-x-auto text-gray-300 font-mono">
                                        {JSON.stringify(trace.steps[selectedStep].input, null, 2)}
                                    </pre>
                                </div>
                            )}

                            {trace.steps[selectedStep].output && (
                                <div>
                                    <div className="text-xs text-gray-500 mb-2 font-medium">Output</div>
                                    <pre className="bg-[#0a0a0a] border border-[#1f1f1f] p-3 rounded-lg text-xs overflow-x-auto text-gray-300 font-mono">
                                        {JSON.stringify(trace.steps[selectedStep].output, null, 2)}
                                    </pre>
                                </div>
                            )}

                            {trace.steps[selectedStep].evaluations &&
                                trace.steps[selectedStep].evaluations.length > 0 && (
                                    <div>
                                        <div className="text-xs text-gray-500 mb-2 font-medium">
                                            Evaluations ({trace.steps[selectedStep].evaluations.length})
                                        </div>
                                        <div className="space-y-2">
                                            {trace.steps[selectedStep].evaluations.map((evaluation, idx) => (
                                                <div key={idx} className="bg-[#0f0f0f] border border-[#1f1f1f] p-3 rounded-lg">
                                                    <div className="flex justify-between items-start mb-2">
                                                        <div>
                                                            <div className="text-sm font-medium text-gray-200">
                                                                {evaluation.label}
                                                            </div>
                                                            <div className="text-xs text-gray-500 mt-0.5">
                                                                {evaluation.item_id}
                                                            </div>
                                                        </div>
                                                        <span
                                                            className={`px-2 py-0.5 rounded-md text-[10px] font-medium ${evaluation.status === 'QUALIFIED' || evaluation.status === 'PASSED'
                                                                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                                                : 'bg-red-500/20 text-red-400 border border-red-500/30'
                                                                }`}
                                                        >
                                                            {evaluation.status}
                                                        </span>
                                                    </div>
                                                    {evaluation.checks && evaluation.checks.length > 0 && (
                                                        <div className="mt-2 space-y-1">
                                                            {evaluation.checks.map((check, checkIdx) => (
                                                                <div
                                                                    key={checkIdx}
                                                                    className={`text-xs flex items-center gap-1 ${check.passed ? 'text-emerald-400' : 'text-red-400'
                                                                        }`}
                                                                >
                                                                    <span>{check.passed ? '✓' : '✗'}</span>
                                                                    <span>{check.name}: {check.detail}</span>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default TraceViewer;
