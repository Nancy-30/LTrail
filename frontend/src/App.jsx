import React, { useState, useEffect, useCallback, useRef } from 'react';
import TraceList from './components/TraceList';
import TraceViewer from './components/TraceViewer';

function App() {
  const [selectedTraceId, setSelectedTraceId] = useState(null);
  const [traces, setTraces] = useState([]);
  const [sidebarWidth, setSidebarWidth] = useState(320);
  const sidebarRef = useRef(null);
  const isResizing = useRef(false);

  const fetchTraces = useCallback(async () => {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/traces?limit=100`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTraces(data.traces || []);
    } catch (error) {
      if (error.message !== 'Failed to fetch') {
        console.error('Failed to fetch traces:', error);
      }
    }
  }, []);

  useEffect(() => {
    fetchTraces();
    const interval = setInterval(fetchTraces, 10000);
    return () => clearInterval(interval);
  }, [fetchTraces]);

  const handleMouseDown = (e) => {
    isResizing.current = true;
    e.preventDefault();
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing.current) return;
      const newWidth = e.clientX;
      if (newWidth >= 200 && newWidth <= 800) {
        setSidebarWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      isResizing.current = false;
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-[#0a0a0a]">
      {/* Header - Langfuse style */}
      <header className="bg-[#111111] border-b border-[#1f1f1f] px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">LT</span>
          </div>
          <div>
            <h1 className="text-base font-semibold text-gray-100">LTrail</h1>
            <p className="text-xs text-gray-500">Decision Observability</p>
          </div>
        </div>
        <div className="text-xs text-gray-500">
          {traces.length} {traces.length === 1 ? 'trace' : 'traces'}
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div
          ref={sidebarRef}
          className="bg-[#111111] border-r border-[#1f1f1f] overflow-y-auto relative"
          style={{ width: `${sidebarWidth}px`, minWidth: '200px', maxWidth: '800px' }}
        >
          <TraceList
            traces={traces}
            selectedTraceId={selectedTraceId}
            onSelectTrace={setSelectedTraceId}
          />
          <div
            className="absolute top-0 right-0 w-1 h-full cursor-col-resize hover:bg-indigo-500/50 bg-transparent transition-colors"
            onMouseDown={handleMouseDown}
          />
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-hidden bg-[#0a0a0a]">
          {selectedTraceId ? (
            <TraceViewer traceId={selectedTraceId} />
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <div className="w-16 h-16 bg-[#1f1f1f] rounded-xl flex items-center justify-center mb-4">
                <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-gray-300 mb-2">No trace selected</h2>
              <p className="text-sm text-gray-500">Select a trace from the sidebar to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
