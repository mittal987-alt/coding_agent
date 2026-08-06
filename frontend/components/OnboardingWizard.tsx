"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, Code2, Database, Terminal, ArrowRight, Loader2 } from "lucide-react";

export default function OnboardingWizard({
  isOpen,
  onComplete,
  projectId
}: {
  isOpen: boolean;
  onComplete: (data: any) => void;
  projectId: string;
}) {
  const [step, setStep] = useState(1);
  const [language, setLanguage] = useState("typescript");
  const [framework, setFramework] = useState("nextjs");
  const [model, setModel] = useState("gpt-4o");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // If closed or already done, don't render
  if (!isOpen) return null;

  const handleFinish = async () => {
    setIsSubmitting(true);
    try {
      // Typically, you'd send this to the backend
      await new Promise(r => setTimeout(r, 800)); // Simulate API call
      onComplete({ language, framework, model });
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="bg-[#1e1e1e] border border-gray-700/80 rounded-2xl p-8 max-w-xl w-full shadow-2xl relative overflow-hidden">
        {/* Decorative background glow */}
        <div className="absolute -top-32 -left-32 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-32 -right-32 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl pointer-events-none" />

        <div className="relative">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-500/20 text-blue-400 mb-4 border border-blue-500/30 shadow-[0_0_15px_rgba(59,130,246,0.2)]">
              <Sparkles size={24} />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Welcome to your new project</h2>
            <p className="text-gray-400 text-sm">Let's set up your agent environment for maximum productivity.</p>
          </div>

          {/* Steps */}
          {step === 1 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
              <div>
                <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 block">
                  Primary Language
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { id: "typescript", name: "TypeScript", icon: <Code2 size={16} className="text-blue-400" /> },
                    { id: "python", name: "Python", icon: <Terminal size={16} className="text-green-400" /> },
                    { id: "rust", name: "Rust", icon: <Database size={16} className="text-orange-400" /> },
                    { id: "go", name: "Go", icon: <Database size={16} className="text-cyan-400" /> },
                  ].map((lang) => (
                    <button
                      key={lang.id}
                      onClick={() => setLanguage(lang.id)}
                      className={`flex items-center gap-3 p-4 rounded-xl border text-sm font-medium transition-all ${
                        language === lang.id
                          ? "bg-blue-600/20 border-blue-500/50 text-white"
                          : "bg-[#252526] border-gray-700/50 text-gray-300 hover:border-gray-600 hover:bg-[#2a2a2b]"
                      }`}
                    >
                      {lang.icon}
                      {lang.name}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex justify-end pt-4">
                <button
                  onClick={() => setStep(2)}
                  className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors shadow-lg shadow-blue-500/20"
                >
                  Continue <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
              <div>
                <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 block">
                  Preferred AI Model
                </label>
                <div className="space-y-3">
                  {[
                    { id: "gpt-4o", name: "GPT-4o (OpenAI)", desc: "Best overall reasoning and coding capabilities." },
                    { id: "claude-3.5-sonnet", name: "Claude 3.5 Sonnet (Anthropic)", desc: "Excellent context window and code generation." },
                    { id: "gemini-1.5-pro", name: "Gemini 1.5 Pro (Google)", desc: "Massive context window for full-repo analysis." },
                  ].map((m) => (
                    <button
                      key={m.id}
                      onClick={() => setModel(m.id)}
                      className={`w-full flex flex-col p-4 rounded-xl border text-left transition-all ${
                        model === m.id
                          ? "bg-blue-600/20 border-blue-500/50"
                          : "bg-[#252526] border-gray-700/50 hover:border-gray-600 hover:bg-[#2a2a2b]"
                      }`}
                    >
                      <span className={`text-sm font-bold mb-1 ${model === m.id ? "text-blue-300" : "text-gray-200"}`}>{m.name}</span>
                      <span className="text-xs text-gray-400">{m.desc}</span>
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex justify-between pt-4">
                <button
                  onClick={() => setStep(1)}
                  className="px-4 py-2.5 text-gray-400 hover:text-white text-sm font-medium transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={handleFinish}
                  disabled={isSubmitting}
                  className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors shadow-lg shadow-blue-500/20"
                >
                  {isSubmitting ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                  Initialize Project
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
