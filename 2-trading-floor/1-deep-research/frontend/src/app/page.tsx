"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Search, Sparkles } from "lucide-react";
import LoadingOverlay from "@/components/LoadingOverlay";
import { useResearchStream } from "@/hooks/useResearchStream";

export default function Home() {
  const router = useRouter();
  const [topic, setTopic] = useState("");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState("");

  // Use the SSE hook for real-time progress
  const { progress } = useResearchStream(taskId);

  // Update status based on real-time progress
  useEffect(() => {
    if (progress) {
      setStatus(progress.current_step);

      if (progress.status === "completed" && progress.result) {
        // Store report and navigate
        localStorage.setItem("researchReport", progress.result);
        localStorage.setItem("researchTopic", topic);
        setIsLoading(false);
        router.push("/report");
      } else if (progress.status === "failed") {
        setIsLoading(false);
        alert(`Research failed: ${progress.error || "Unknown error"}`);
        setTaskId(null);
      }
    }
  }, [progress, router, topic]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsLoading(true);
    setStatus("Starting research...");

    try {
      const response = await fetch("http://127.0.0.1:8000/research", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic }),
      });

      if (!response.ok) {
        throw new Error("Failed to start research");
      }

      const data = await response.json();
      setTaskId(data.task_id);
    } catch (error) {
      console.error(error);
      alert("Failed to start research. Please try again.");
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white selection:bg-blue-500/30">
      <LoadingOverlay isLoading={isLoading} status={status} />

      <main className="container mx-auto px-4 h-screen flex flex-col items-center justify-center relative overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-blue-500/20 rounded-full blur-[100px] -z-10" />
        <div className="absolute top-0 left-0 w-full h-full bg-[url('/grid.svg')] opacity-10 -z-10" />

        <div className="text-center w-full max-w-3xl space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-1000">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-700 text-sm text-zinc-400 mb-4">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <span>Powered by CrewAI Agents</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-white to-white/50 tracking-tight">
            Deep Research Agent
          </h1>

          <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
            Autonomous agent that plans, searches, reads, and synthesizes
            information to create deep, comprehensive reports.
          </p>

          <form onSubmit={handleSubmit} className="relative max-w-2xl mx-auto w-full group">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition-opacity" />

            <div className="relative flex items-center bg-zinc-900 rounded-2xl border border-zinc-700 shadow-2xl p-2 transition-transform group-hover:scale-[1.01]">
              <Search className="w-6 h-6 text-zinc-500 ml-4" />
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="What would you like to research today?"
                className="w-full bg-transparent border-none focus:ring-0 text-lg px-4 py-3 placeholder-zinc-600"
                autoFocus
              />
              <button
                type="submit"
                disabled={isLoading || !topic.trim()}
                className="bg-white text-black px-6 py-3 rounded-xl font-medium hover:bg-zinc-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <span>Research</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          <div className="flex flex-wrap justify-center gap-3 text-sm text-zinc-500 mt-8">
            <span className="text-zinc-600">Try asking:</span>
            {["Future of AI Agents", "Quantum Computing Trends", "CRISPR Developments"].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => setTopic(suggestion)}
                className="hover:text-white transition-colors border-b border-dotted border-zinc-700 hover:border-white"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
