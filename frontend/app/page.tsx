import React from "react";
import Link from "next/link";
import { ArrowRight, Bot, Code2, Zap } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50 dark:bg-black font-sans">
      <main className="flex flex-1 flex-col items-center justify-center py-20 px-6 sm:px-12 text-center">
        <div className="mb-8 flex items-center justify-center p-4 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-2xl shadow-sm">
          <Bot size={48} />
        </div>
        
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-gray-900 dark:text-white mb-6">
          AI Software Engineering <br className="hidden sm:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">
            Assistant
          </span>
        </h1>
        
        <p className="max-w-2xl text-lg sm:text-xl text-gray-600 dark:text-gray-400 mb-10 leading-relaxed">
          Connect your GitHub repository and let autonomous AI agents like Mistral or Claude edit, refactor, and manage your codebase. Accelerate your workflow with intelligent code generation and autonomous problem solving.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 items-center">
          <Link
            href="/projects"
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-8 py-3.5 rounded-full font-medium transition-all shadow-lg shadow-blue-600/30 hover:shadow-blue-600/40 hover:-translate-y-0.5 text-lg"
          >
            Go to Projects
            <ArrowRight size={20} />
          </Link>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-900 dark:text-white px-8 py-3.5 rounded-full font-medium transition-all text-lg"
          >
            Documentation
          </a>
        </div>

        <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl text-left">
          <div className="bg-white dark:bg-gray-900 p-8 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
            <div className="bg-blue-100 dark:bg-blue-900/30 w-12 h-12 rounded-xl flex items-center justify-center text-blue-600 dark:text-blue-400 mb-6">
              <Code2 size={24} />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Multi-Framework</h3>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              Supports any language or framework. The AI assistant automatically detects your stack and sets up the environment.
            </p>
          </div>
          <div className="bg-white dark:bg-gray-900 p-8 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
            <div className="bg-purple-100 dark:bg-purple-900/30 w-12 h-12 rounded-xl flex items-center justify-center text-purple-600 dark:text-purple-400 mb-6">
              <Bot size={24} />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Autonomous Agents</h3>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              Deploy agents that can read code, execute terminal commands, edit files, and run tests entirely autonomously.
            </p>
          </div>
          <div className="bg-white dark:bg-gray-900 p-8 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
            <div className="bg-green-100 dark:bg-green-900/30 w-12 h-12 rounded-xl flex items-center justify-center text-green-600 dark:text-green-400 mb-6">
              <Zap size={24} />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">Instant Setup</h3>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              Create a new project in seconds. The workspace, vector stores, and memory are configured instantly.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
