import { useState, useEffect } from 'react';

interface Progress {
  status: string;
  current_step: string;
  percent: number;
  result: string | null;
  error: string | null;
}

interface UseResearchStreamResult {
  progress: Progress | null;
  isConnected: boolean;
}

/**
 * Hook to stream real-time research progress via Server-Sent Events (SSE)
 * @param taskId - The task ID to stream progress for
 * @returns Progress data and connection status
 */
export function useResearchStream(taskId: string | null): UseResearchStreamResult {
  const [progress, setProgress] = useState<Progress | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!taskId) {
      setProgress(null);
      setIsConnected(false);
      return;
    }

    const eventSource = new EventSource(
      `http://127.0.0.1:8000/research/${taskId}/stream`
    );

    eventSource.onopen = () => {
      console.log('SSE connection opened');
      setIsConnected(true);
    };

    eventSource.addEventListener('progress', (e) => {
      const data = JSON.parse(e.data) as Progress;
      console.log('Progress update:', data);
      setProgress(data);
    });

    eventSource.addEventListener('ping', () => {
      // Keepalive - do nothing
      console.log('Keepalive ping received');
    });

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      setIsConnected(false);
      eventSource.close();
    };

    // Cleanup on unmount or taskId change
    return () => {
      console.log('Closing SSE connection');
      eventSource.close();
      setIsConnected(false);
    };
  }, [taskId]);

  return { progress, isConnected };
}
