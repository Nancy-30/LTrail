import { useEffect, useRef } from 'react';

/**
 * Custom hook for polling traces with smart interval management
 * Reduces polling frequency when no changes detected
 */
export function useTracePolling(fetchTraces, enabled = true) {
  const lastTraceCountRef = useRef(0);
  const intervalRef = useRef(null);
  const consecutiveNoChangeRef = useRef(0);

  useEffect(() => {
    if (!enabled) return;

    const poll = async () => {
      const previousCount = lastTraceCountRef.current;
      await fetchTraces();
      
      // Check if trace count changed
      // This is a simple optimization - in production you'd compare trace IDs
      const currentCount = document.querySelectorAll('[data-trace-id]')?.length || 0;
      
      if (currentCount === previousCount) {
        consecutiveNoChangeRef.current += 1;
        // Increase interval if no changes for a while (up to 30 seconds max)
        if (consecutiveNoChangeRef.current > 3) {
          const newInterval = Math.min(30000, 10000 * (1 + consecutiveNoChangeRef.current / 3));
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = setInterval(poll, newInterval);
          }
        }
      } else {
        consecutiveNoChangeRef.current = 0;
        // Reset to fast polling when changes detected
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = setInterval(poll, 10000);
        }
      }
      
      lastTraceCountRef.current = currentCount;
    };

    // Initial fetch
    poll();
    
    // Start polling every 10 seconds
    intervalRef.current = setInterval(poll, 10000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, fetchTraces]);
}

