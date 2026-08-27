import React from "react";
import Link from "next/link";
import {
  ArrowRight,
  Bot,
  Code2,
  Zap,
  Sparkles,
  Terminal,
  GitBranch,
  Brain,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen overflow-hidden bg-[#f8f8fc] text-[#111118] selection:bg-indigo-500 selection:text-white">

      {/* =========================================================
          BACKGROUND
      ========================================================= */}

      <div className="pointer-events-none fixed inset-0 overflow-hidden">

        {/* Main glow */}
        <div className="absolute left-1/2 top-[-180px] h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-indigo-400/10 blur-[130px]" />

        {/* Left glow */}
        <div className="absolute left-[5%] top-[35%] h-[300px] w-[300px] rounded-full bg-cyan-300/10 blur-[120px]" />

        {/* Right glow */}
        <div className="absolute right-[5%] top-[55%] h-[350px] w-[350px] rounded-full bg-violet-300/10 blur-[130px]" />

        {/* Grid */}
        <div
          className="absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage:
              "linear-gradient(#6366f1 1px, transparent 1px), linear-gradient(90deg, #6366f1 1px, transparent 1px)",
            backgroundSize: "48px 48px",
          }}
        />
      </div>

      {/* =========================================================
          NAVBAR
      ========================================================= */}

      <header className="relative z-20 mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-5 sm:px-10">

        {/* Logo */}
        <Link href="/" className="flex items-center gap-3">

          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#17171f] text-indigo-400 shadow-lg shadow-black/10">
            <Bot size={21} strokeWidth={2.2} />
          </div>

          <div className="flex items-center">
            <span className="text-[17px] font-bold tracking-[-0.02em]">
              CodeVerse
            </span>

            <span className="ml-2 hidden rounded-full border border-indigo-200 bg-indigo-50 px-2 py-0.5 text-[9px] font-semibold uppercase tracking-wider text-indigo-600 sm:inline-block">
              AI
            </span>
          </div>

        </Link>

        {/* Navigation */}
        <nav className="hidden items-center gap-8 md:flex">

          <Link
            href="#features"
            className="text-sm font-medium text-gray-500 transition hover:text-gray-950"
          >
            Features
          </Link>

          <Link
            href="#workflow"
            className="text-sm font-medium text-gray-500 transition hover:text-gray-950"
          >
            How it works
          </Link>

          <Link
            href="#agents"
            className="text-sm font-medium text-gray-500 transition hover:text-gray-950"
          >
            Agents
          </Link>

        </nav>

        {/* Right Navigation */}
        <div className="flex items-center gap-3">

          <Link
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition hover:bg-white hover:text-gray-950 sm:flex"
          >

            <svg
              className="h-4 w-4"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>

            GitHub
          </Link>

          <Link
            href="/projects"
            className="rounded-xl bg-[#17171f] px-5 py-2.5 text-sm font-semibold text-white shadow-md transition hover:-translate-y-0.5 hover:bg-black"
          >
            Get Started
          </Link>

        </div>
      </header>

      {/* =========================================================
          MAIN
      ========================================================= */}

      <main className="relative z-10">

        {/* =======================================================
            HERO
        ======================================================= */}

        <section className="mx-auto flex max-w-6xl flex-col items-center px-6 pb-16 pt-20 text-center sm:px-10 sm:pt-28">

          {/* Badge */}

          <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-white/80 px-4 py-2 text-xs font-semibold text-indigo-600 shadow-sm backdrop-blur">

            <Sparkles size={14} />

            <span>
              Autonomous AI Software Engineering
            </span>

            <ArrowRight size={13} />

          </div>

          {/* Heading */}

          <h1 className="max-w-5xl text-[48px] font-extrabold leading-[0.98] tracking-[-0.055em] sm:text-[72px] lg:text-[88px]">

            Your AI engineer

            <br />

            <span className="bg-gradient-to-r from-indigo-600 via-blue-500 to-cyan-400 bg-clip-text text-transparent">
              for every codebase.
            </span>

          </h1>

          {/* Description */}

          <p className="mt-8 max-w-2xl text-base leading-7 text-gray-500 sm:text-lg">

            Connect your repository and let intelligent agents understand,
            modify, debug, refactor, test, and improve your entire codebase.

          </p>

          {/* CTA */}

          <div className="mt-9 flex w-full flex-col items-center justify-center gap-3 sm:w-auto sm:flex-row">

            <Link
              href="/projects"
              className="group flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-7 py-3.5 text-sm font-semibold text-white shadow-xl shadow-indigo-500/20 transition hover:-translate-y-0.5 hover:bg-indigo-700 sm:w-auto"
            >

              Start Building

              <ArrowRight
                size={17}
                className="transition-transform group-hover:translate-x-1"
              />

            </Link>

            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-gray-200 bg-white px-7 py-3.5 text-sm font-semibold text-gray-800 shadow-sm transition hover:-translate-y-0.5 hover:border-gray-300 hover:bg-gray-50 sm:w-auto"
            >
              View Documentation
            </a>

          </div>

          {/* Trust */}

          <div className="mt-7 flex flex-wrap items-center justify-center gap-2 text-xs text-gray-400">

            <ShieldCheck size={14} />

            Secure sandboxed execution

            <span>•</span>

            GitHub integration

            <span>•</span>

            Human approval

          </div>

        </section>

        {/* =======================================================
            PRODUCT PREVIEW
        ======================================================= */}

        <section className="relative mx-auto max-w-6xl px-6 sm:px-10">

          <div className="relative overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-[0_30px_80px_-30px_rgba(0,0,0,0.25)]">

            {/* Window Header */}

            <div className="flex items-center justify-between border-b border-gray-200 bg-[#fafafa] px-4 py-3">

              <div className="flex items-center gap-1.5">

                <div className="h-2.5 w-2.5 rounded-full bg-red-400" />

                <div className="h-2.5 w-2.5 rounded-full bg-yellow-400" />

                <div className="h-2.5 w-2.5 rounded-full bg-green-400" />

              </div>

              <div className="hidden items-center gap-2 rounded-md border border-gray-200 bg-white px-4 py-1.5 text-[11px] text-gray-400 sm:flex">

                <GitBranch size={12} />

                main

              </div>

              <div className="text-[11px] font-medium text-gray-400">
                CodeVerse Workspace
              </div>

            </div>

            {/* Workspace */}

            <div className="grid min-h-[360px] grid-cols-1 lg:grid-cols-[190px_1fr_270px]">

              {/* =================================================
                  FILE EXPLORER
              ================================================= */}

              <div className="hidden border-r border-gray-200 bg-[#fafafa] p-4 lg:block">

                <div className="mb-4 text-[10px] font-bold uppercase tracking-widest text-gray-400">
                  Explorer
                </div>

                <div className="space-y-1 text-xs">

                  {[
                    "src",
                    "components",
                    "lib",
                    "api",
                    "package.json",
                    "README.md",
                  ].map((item, index) => (

                    <div
                      key={item}
                      className={`rounded-md px-3 py-2 ${
                        index === 1
                          ? "bg-indigo-50 font-medium text-indigo-600"
                          : "text-gray-500"
                      }`}
                    >
                      {item}
                    </div>

                  ))}

                </div>

              </div>

              {/* =================================================
                  CODE EDITOR
              ================================================= */}

              <div className="bg-[#101116] p-5 text-left font-mono text-xs leading-6 text-gray-400">

                <div className="mb-4 flex items-center justify-between border-b border-white/5 pb-3">

                  <span className="text-gray-300">
                    components/AgentPanel.tsx
                  </span>

                  <span className="rounded bg-emerald-500/10 px-2 py-1 text-[10px] text-emerald-400">
                    Modified
                  </span>

                </div>

                <div>

                  <span className="text-purple-400">
                    export
                  </span>{" "}

                  <span className="text-blue-400">
                    default
                  </span>{" "}

                  <span className="text-yellow-300">
                    function
                  </span>{" "}

                  <span className="text-cyan-300">
                    AgentPanel
                  </span>

                  <span className="text-gray-400">
                    () {"{"}
                  </span>

                </div>

                <div className="pl-5">

                  <span className="text-purple-400">
                    const
                  </span>{" "}

                  <span className="text-cyan-300">
                    agent
                  </span>{" "}

                  ={" "}

                  <span className="text-green-400">
                    useCodingAgent()
                  </span>;

                </div>

                <div className="pl-5">

                  <span className="text-purple-400">
                    return
                  </span>{" "}

                  <span className="text-gray-300">
                    {"("}
                  </span>

                </div>

                <div className="pl-10 text-gray-500">
                  {"<AgentWorkspace"}
                </div>

                <div className="pl-16">

                  <span className="text-indigo-400">
                    repository
                  </span>

                  ={" "}

                  <span className="text-green-400">
                    "my-project"
                  </span>

                </div>

                <div className="pl-16">

                  <span className="text-indigo-400">
                    autonomous
                  </span>

                  ={" "}

                  <span className="text-orange-400">
                    {"true"}
                  </span>

                </div>

                <div className="pl-10 text-gray-500">
                  {"/>"}
                </div>

                <div className="pl-5 text-gray-300">
                  {")"}
                </div>

                <div>
                  {"}"}
                </div>

                {/* Agent status */}

                <div className="mt-4 flex items-center gap-2 text-[10px] text-gray-600">

                  <span className="h-3 w-[2px] animate-pulse bg-indigo-400" />

                  Agent is editing your code...

                </div>

              </div>

              {/* =================================================
                  AGENT PANEL
              ================================================= */}

              <div className="border-l border-gray-200 bg-white p-5 text-left">

                {/* Agent header */}

                <div className="mb-5 flex items-center gap-3">

                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                    <Bot size={18} />
                  </div>

                  <div>

                    <div className="text-sm font-semibold">
                      Coding Agent
                    </div>

                    <div className="flex items-center gap-1 text-[10px] text-emerald-500">

                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />

                      Working

                    </div>

                  </div>

                </div>

                {/* Agent tasks */}

                <div className="space-y-3">

                  {[
                    "Analyzing repository",
                    "Finding related components",
                    "Updating AgentPanel.tsx",
                    "Running tests",
                  ].map((item, index) => (

                    <div
                      key={item}
                      className="flex items-center gap-3 rounded-lg bg-gray-50 px-3 py-2.5"
                    >

                      <CheckCircle2
                        size={14}
                        className={
                          index < 3
                            ? "text-emerald-500"
                            : "text-gray-300"
                        }
                      />

                      <span className="text-[11px] text-gray-600">
                        {item}
                      </span>

                    </div>

                  ))}

                </div>

                {/* Insight */}

                <div className="mt-6 rounded-xl border border-indigo-100 bg-indigo-50/60 p-4">

                  <div className="flex items-center gap-2 text-xs font-semibold text-indigo-700">

                    <Sparkles size={13} />

                    Agent Insight

                  </div>

                  <p className="mt-2 text-[11px] leading-5 text-indigo-600/70">

                    Found 3 related components and identified
                    one duplicated state management pattern.

                  </p>

                </div>

              </div>

            </div>

          </div>

          {/* Glow */}

          <div className="absolute -bottom-20 left-1/2 -z-10 h-40 w-2/3 -translate-x-1/2 rounded-full bg-indigo-500/20 blur-[90px]" />

        </section>

        {/* =======================================================
            FEATURES
        ======================================================= */}

        <section
          id="features"
          className="mx-auto max-w-6xl px-6 pb-24 pt-28 sm:px-10"
        >

          <div className="mb-12 max-w-2xl">

            <div className="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-indigo-600">
              Built for developers
            </div>

            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Everything your AI engineer needs.
            </h2>

            <p className="mt-4 text-sm leading-6 text-gray-500 sm:text-base">

              From understanding an unfamiliar repository to shipping
              production-ready changes, CodeVerse handles the workflow.

            </p>

          </div>

          <div className="grid gap-5 md:grid-cols-3">

            {/* Feature 1 */}

            <div className="group rounded-2xl border border-gray-200 bg-white p-7 shadow-sm transition duration-300 hover:-translate-y-1 hover:border-indigo-200 hover:shadow-xl hover:shadow-indigo-500/5">

              <div className="mb-6 flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 transition group-hover:scale-110">
                <Code2 size={21} />
              </div>

              <h3 className="text-lg font-bold">
                Understand Any Codebase
              </h3>

              <p className="mt-3 text-sm leading-6 text-gray-500">

                Automatically analyze project structure, dependencies,
                frameworks, and existing implementation patterns.

              </p>

            </div>

            {/* Feature 2 */}

            <div className="group rounded-2xl border border-gray-200 bg-white p-7 shadow-sm transition duration-300 hover:-translate-y-1 hover:border-indigo-200 hover:shadow-xl hover:shadow-indigo-500/5">

              <div className="mb-6 flex h-11 w-11 items-center justify-center rounded-xl bg-violet-50 text-violet-600 transition group-hover:scale-110">
                <Brain size={21} />
              </div>

              <h3 className="text-lg font-bold">
                Autonomous Agents
              </h3>

              <p className="mt-3 text-sm leading-6 text-gray-500">

                Agents can reason over your repository, modify files,
                execute commands, investigate errors, and iterate.

              </p>

            </div>

            {/* Feature 3 */}

            <div className="group rounded-2xl border border-gray-200 bg-white p-7 shadow-sm transition duration-300 hover:-translate-y-1 hover:border-indigo-200 hover:shadow-xl hover:shadow-indigo-500/5">

              <div className="mb-6 flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-50 text-cyan-600 transition group-hover:scale-110">
                <Zap size={21} />
              </div>

              <h3 className="text-lg font-bold">
                Build Faster
              </h3>

              <p className="mt-3 text-sm leading-6 text-gray-500">

                Go from idea to working implementation faster with
                automated coding, testing, debugging, and refactoring.

              </p>

            </div>

          </div>

        </section>

        {/* =======================================================
            WORKFLOW
        ======================================================= */}

        <section
          id="workflow"
          className="border-y border-gray-200 bg-white"
        >

          <div className="mx-auto max-w-6xl px-6 py-24 sm:px-10">

            <div className="grid items-center gap-16 lg:grid-cols-2">

              {/* Left */}

              <div>

                <div className="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-indigo-600">
                  Simple workflow
                </div>

                <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">

                  Give the agent a task.

                  <br />

                  Let it do the work.

                </h2>

                <p className="mt-5 max-w-lg text-sm leading-6 text-gray-500 sm:text-base">

                  CodeVerse turns a natural-language request into a
                  complete engineering workflow.

                </p>

              </div>

              {/* Right */}

              <div className="space-y-4">

                {[
                  {
                    icon: GitBranch,
                    title: "Connect repository",
                    text: "Import your GitHub project and index the codebase.",
                  },
                  {
                    icon: Brain,
                    title: "Describe the task",
                    text: "Tell the agent what you want to build or fix.",
                  },
                  {
                    icon: Terminal,
                    title: "Agent executes",
                    text: "Read, plan, edit, run commands, and test.",
                  },
                  {
                    icon: CheckCircle2,
                    title: "Review changes",
                    text: "Inspect the generated changes before shipping.",
                  },
                ].map((item, index) => {

                  const Icon = item.icon;

                  return (
                    <div
                      key={item.title}
                      className="flex gap-4 rounded-xl border border-gray-200 bg-gray-50 p-4"
                    >

                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-white text-indigo-600 shadow-sm">
                        <Icon size={18} />
                      </div>

                      <div>

                        <div className="text-sm font-semibold">
                          {index + 1}. {item.title}
                        </div>

                        <div className="mt-1 text-xs leading-5 text-gray-500">
                          {item.text}
                        </div>

                      </div>

                    </div>
                  );
                })}

              </div>

            </div>

          </div>

        </section>

        {/* =======================================================
            AGENTS SECTION
        ======================================================= */}

        <section
          id="agents"
          className="mx-auto max-w-6xl px-6 py-24 sm:px-10"
        >

          <div className="rounded-3xl border border-gray-200 bg-white p-8 shadow-sm sm:p-12">

            <div className="grid items-center gap-12 lg:grid-cols-2">

              <div>

                <div className="mb-3 text-xs font-bold uppercase tracking-[0.2em] text-indigo-600">
                  Multi-agent architecture
                </div>

                <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                  More than one AI agent.
                </h2>

                <p className="mt-5 text-sm leading-6 text-gray-500 sm:text-base">

                  CodeVerse can coordinate specialized agents for
                  planning, coding, debugging, testing, and code review.

                </p>

                <Link
                  href="/projects"
                  className="mt-7 inline-flex items-center gap-2 rounded-xl bg-gray-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-black"
                >
                  Explore Agents
                  <ArrowRight size={16} />
                </Link>

              </div>

              {/* Agent cards */}

              <div className="grid gap-3 sm:grid-cols-2">

                {[
                  {
                    title: "Planner",
                    description: "Breaks complex tasks into steps.",
                  },
                  {
                    title: "Coder",
                    description: "Implements the required changes.",
                  },
                  {
                    title: "Debugger",
                    description: "Finds and fixes implementation issues.",
                  },
                  {
                    title: "Tester",
                    description: "Runs tests and validates changes.",
                  },
                ].map((agent) => (

                  <div
                    key={agent.title}
                    className="rounded-xl border border-gray-200 bg-gray-50 p-5 transition hover:border-indigo-200 hover:bg-indigo-50/40"
                  >

                    <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg bg-white text-indigo-600 shadow-sm">
                      <Bot size={17} />
                    </div>

                    <h3 className="text-sm font-bold">
                      {agent.title}
                    </h3>

                    <p className="mt-1 text-xs leading-5 text-gray-500">
                      {agent.description}
                    </p>

                  </div>

                ))}

              </div>

            </div>

          </div>

        </section>

        {/* =======================================================
            FINAL CTA
        ======================================================= */}

        <section className="mx-auto max-w-6xl px-6 pb-24 sm:px-10">

          <div className="relative overflow-hidden rounded-3xl bg-[#111118] px-7 py-16 text-center sm:px-12">

            {/* Glow */}

            <div className="absolute left-1/2 top-0 h-48 w-96 -translate-x-1/2 rounded-full bg-indigo-600/30 blur-[90px]" />

            <div className="relative">

              <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-white/10 text-indigo-300">
                <Bot size={23} />
              </div>

              <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">

                Your next engineer is already here.

              </h2>

              <p className="mx-auto mt-4 max-w-xl text-sm leading-6 text-gray-400">

                Connect your repository and start building with
                CodeVerse, your autonomous AI software engineering assistant.

              </p>

              <Link
                href="/projects"
                className="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3.5 text-sm font-semibold text-gray-950 transition hover:-translate-y-0.5 hover:bg-gray-100"
              >

                Open CodeVerse

                <ArrowRight size={16} />

              </Link>

            </div>

          </div>

        </section>

      </main>

      {/* =========================================================
          FOOTER
      ========================================================= */}

      <footer className="border-t border-gray-200 bg-white">

        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-6 py-7 text-xs text-gray-400 sm:flex-row sm:px-10">

          <div className="flex items-center gap-2">

            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-[#17171f] text-indigo-400">
              <Bot size={13} />
            </div>

            <span>
              © {new Date().getFullYear()} CodeVerse
            </span>

          </div>

          <div className="flex items-center gap-5">

            <span>
              AI-powered development
            </span>

            <span>•</span>

            <span>
              Built for developers
            </span>

          </div>

        </div>

      </footer>

    </div>
  );
}