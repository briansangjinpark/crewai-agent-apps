"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { ArrowLeft, Copy, Check } from "lucide-react";

export default function ReportPage() {
    const router = useRouter();
    const [report, setReport] = useState("");
    const [topic, setTopic] = useState("");
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        // Retrieve report from localStorage
        const savedReport = localStorage.getItem("researchReport");
        const savedTopic = localStorage.getItem("researchTopic");

        if (!savedReport) {
            router.push("/");
            return;
        }

        setReport(savedReport);
        setTopic(savedTopic || "Research Report");
    }, [router]);

    const handleCopy = () => {
        navigator.clipboard.writeText(report);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="min-h-screen bg-black text-zinc-100">
            <nav className="border-b border-zinc-800 bg-black/50 backdrop-blur-md sticky top-0 z-40">
                <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                    <button
                        onClick={() => router.push("/")}
                        className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        <span>New Search</span>
                    </button>

                    <div className="font-medium truncate max-w-md hidden md:block text-zinc-400">
                        {topic}
                    </div>

                    <button
                        onClick={handleCopy}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-sm font-medium transition-colors"
                    >
                        {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                        <span>{copied ? "Copied" : "Copy Markdown"}</span>
                    </button>
                </div>
            </nav>

            <main className="container mx-auto px-4 py-12 max-w-4xl">
                <article className="prose prose-invert prose-lg max-w-none prose-headings:text-white prose-a:text-blue-400 hover:prose-a:text-blue-300">
                    <ReactMarkdown>{report}</ReactMarkdown>
                </article>
            </main>
        </div>
    );
}
