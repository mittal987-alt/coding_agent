import React from "react";
import Link from "next/link";
import { ArrowRight, Bot, Code2, Zap, Sparkles, Terminal } from "lucide-react";

export default function Home() {
  return (
    <div className="relative flex flex-col min-h-screen bg-background text-foreground font-sans overflow-hidden selection:bg-accent selection:text-white">
      
      {/* Subtle Glow Elements */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[300px] bg-accent/10 blur-[120px] rounded-full pointer-events-none" />

      {/* Navigation Header */}
      <header className="relative z-10 flex items-center justify-between px-6 sm:px-12 py-6 max-w-7xl mx-auto w-full">
        <div className="flex items-center gap-3">
          <div className="p-2 glass rounded-xl text-accent">
            <Bot size={22} />
          </div>
          <span className="font-bold text-lg tracking-tight text-text-primary">
            AgentCode
          </span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="https://github.com"
            target="_blank"
            className="hidden sm:flex items-center gap-2 text-sm text-text-secondary hover:text-text-primary transition-colors"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>
            GitHub
          </Link>
          <Link
            href="/projects"
            className="text-sm font-medium glass px-4 py-2 rounded-full hover:bg-surface-hover transition-all shadow-sm text-text-primary"
          >
            Sign In
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="relative z-10 flex flex-1 flex-col items-center justify-center py-16 px-6 sm:px-12 text-center max-w-5xl mx-auto">
        
        {/* Announcement Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full glass-panel text-accent text-xs sm:text-sm font-medium mb-8 shadow-inner">
          <Sparkles size={14} className="text-accent animate-pulse" />
          <span>Introducing Autonomous Multi-Agent Workflows</span>
          <ArrowRight size={14} className="opacity-70" />
        </div>
        
        {/* Main Heading */}
        <h1 className="text-4xl sm:text-7xl font-extrabold tracking-tight text-text-primary mb-6 leading-[1.1]">
          AI Software Engineering <br className="hidden sm:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-cyan-400">
            Assistant for Codebases
          </span>
        </h1>
        
        {/* Subtitle */}
        <p className="max-w-2xl text-base sm:text-lg text-text-secondary mb-10 leading-relaxed font-normal">
          Connect your GitHub repository and let autonomous AI agents like Mistral or Claude edit, refactor, and manage your codebase with human-like precision.
        </p>
        
        {/* Call to Actions */}
        <div className="flex flex-col sm:flex-row gap-4 items-center w-full sm:w-auto">
          <Link
            href="/projects"
            className="w-full sm:w-auto flex items-center justify-center gap-2 bg-accent hover:bg-accent-hover text-white px-8 py-4 rounded-full font-semibold transition-all shadow-lg shadow-blue-500/20 hover:-translate-y-0.5 text-base"
          >
            Go to Projects
            <ArrowRight size={18} />
          </Link>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="w-full sm:w-auto flex items-center justify-center gap-2 glass px-8 py-4 rounded-full font-semibold transition-all text-base text-text-primary hover:bg-surface-hover"
          >
            Read Documentation
          </a>
        </div>

        {/* Feature Cards Grid */}
        <div className="mt-28 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl text-left w-full">
          
          {/* Card 1 */}
          <div className="glass p-8 rounded-2xl hover:bg-surface-hover transition-all duration-300 shadow-xl group">
            <div className="bg-surface-2 border border-border-subtle w-12 h-12 rounded-xl flex items-center justify-center text-accent mb-6 group-hover:scale-110 transition-transform">
              <Code2 size={22} />
            </div>
            <h3 className="text-xl font-bold text-text-primary mb-3">Multi-Framework</h3>
            <p className="text-text-muted text-sm leading-relaxed">
              Supports any language or framework. The AI assistant automatically detects your stack and configures the workspace.
            </p>
          </div>

          {/* Card 2 */}
          <div className="glass p-8 rounded-2xl hover:bg-surface-hover transition-all duration-300 shadow-xl group">
            <div className="bg-surface-2 border border-border-subtle w-12 h-12 rounded-xl flex items-center justify-center text-accent mb-6 group-hover:scale-110 transition-transform">
              <Terminal size={22} />
            </div>
            <h3 className="text-xl font-bold text-text-primary mb-3">Autonomous Agents</h3>
            <p className="text-text-muted text-sm leading-relaxed">
              Deploy agents that can read codebases, execute secure terminal commands, edit files, and run tests independently.
            </p>
          </div>

          {/* Card 3 */}
          <div className="glass p-8 rounded-2xl hover:bg-surface-hover transition-all duration-300 shadow-xl group">
            <div className="bg-surface-2 border border-border-subtle w-12 h-12 rounded-xl flex items-center justify-center text-accent mb-6 group-hover:scale-110 transition-transform">
              <Zap size={22} />
            </div>
            <h3 className="text-xl font-bold text-text-primary mb-3">Instant Setup</h3>
            <p className="text-text-muted text-sm leading-relaxed">
              Create a new project in seconds. Vector stores, long-term memory, and sandbox environments are set up automatically.
            </p>
          </div>

        </div>

      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border-subtle py-8 text-center text-xs text-text-muted">
        <p>© {new Date().getFullYear()} AgentCode Inc. Built for high-performance software engineering teams.</p>
      </footer>

    </div>
  );
}