import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingOverlayProps {
    isLoading: boolean;
    status: string;
}

export default function LoadingOverlay({ isLoading, status }: LoadingOverlayProps) {
    if (!isLoading) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex flex-col items-center justify-center text-white">
            <div className="bg-zinc-900 p-8 rounded-2xl shadow-2xl flex flex-col items-center border border-zinc-800">
                <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
                <h3 className="text-xl font-bold mb-2">Deep Research Agent</h3>
                <p className="text-zinc-400 animate-pulse">{status}</p>

                <div className="mt-6 flex flex-col gap-2 w-64">
                    {/* Visual progress steps could go here */}
                    <div className="h-1 w-full bg-zinc-800 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500 animate-progress origin-left w-full"></div>
                    </div>
                </div>
            </div>
        </div>
    );
}
