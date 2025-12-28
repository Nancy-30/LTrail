import React from 'react';

function TraceList({ traces, selectedTraceId, onSelectTrace }) {
    const getStatusColor = (status) => {
        switch (status) {
            case 'completed':
                return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
            case 'error':
                return 'bg-red-500/20 text-red-400 border-red-500/30';
            case 'in_progress':
                return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
            default:
                return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    };

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="px-4 py-4 border-b border-[#1f1f1f]">
                <h2 className="text-sm font-semibold text-gray-200 mb-1">Traces</h2>
                <p className="text-xs text-gray-500">View execution history</p>
            </div>

            {/* Trace List */}
            <div className="flex-1 overflow-y-auto">
                {traces.length === 0 ? (
                    <div className="p-8 text-center">
                        <div className="w-12 h-12 bg-[#1f1f1f] rounded-lg flex items-center justify-center mx-auto mb-3">
                            <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        </div>
                        <p className="text-sm font-medium text-gray-400 mb-1">No traces yet</p>
                        <p className="text-xs text-gray-600">
                            Run your application with LTrail SDK
                        </p>
                    </div>
                ) : (
                    <div className="p-2">
                        {traces.map((trace) => (
                            <div
                                key={trace.trace_id}
                                onClick={() => onSelectTrace(trace.trace_id)}
                                className={`group relative mb-2 p-3 rounded-lg border cursor-pointer transition-all ${selectedTraceId === trace.trace_id
                                    ? 'bg-[#1a1a1a] border-indigo-500/50 shadow-lg shadow-indigo-500/10'
                                    : 'bg-[#0f0f0f] border-[#1f1f1f] hover:bg-[#151515] hover:border-[#2a2a2a]'
                                    }`}
                            >
                                {/* Trace Name */}
                                <div className="flex items-start justify-between gap-2 mb-2">
                                    <h3 className="text-sm font-medium text-gray-200 flex-1 line-clamp-2 group-hover:text-gray-100 transition-colors">
                                        {trace.name}
                                    </h3>
                                    <span
                                        className={`px-2 py-0.5 rounded-md text-[10px] font-medium border flex-shrink-0 ${getStatusColor(trace.status)}`}
                                    >
                                        {trace.status}
                                    </span>
                                </div>

                                {/* Metadata */}
                                <div className="flex items-center gap-3 text-xs text-gray-500 mb-2">
                                    <span className="flex items-center gap-1">
                                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                        </svg>
                                        {trace.step_count || 0} steps
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                        </svg>
                                        {formatDate(trace.created_at)}
                                    </span>
                                </div>

                                {/* Trace ID */}
                                <div className="mt-2 pt-2 border-t border-[#1f1f1f]">
                                    <code className="text-[10px] text-gray-600 font-mono">
                                        {trace.trace_id.substring(0, 16)}...
                                    </code>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default TraceList;
