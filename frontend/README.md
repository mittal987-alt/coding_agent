# 💻 AI Software Engineer - Web Workspace Frontend

This is the Next.js 16 web interface for the **AI Software Engineer** platform. It provides a full-featured browser IDE workspace with a Monaco Code Editor, resizable split panels, real-time WebSocket terminal, and interactive AI agent chat.

## 🚀 Features

- 📝 **Monaco Code Editor**: Code editing with syntax highlighting, language support, and real-time diff preview.
- 🖥️ **Streaming Xterm.js Terminal**: Web-based interactive terminal over WebSockets (`ws://`).
- 🤖 **AI Chat Workspace**: Real-time agent streaming, code snippet insertion, and plan inspection.
- 🎨 **Modern Dark Mode UI**: Styled with Tailwind CSS v4, Material UI, and Lucide icons.
- ⚡ **TanStack Query & Zustand**: State management for workspace state, file trees, and active sessions.

## 📦 Scripts

- `npm run dev`: Starts the Next.js development server on `http://localhost:3000`.
- `npm run build`: Compiles the production build.
- `npm run start`: Runs the built production server.
- `npm run lint`: Runs ESLint checks.

## ⚙️ Environment Variables

Create a `.env.local` file in this directory with the following configuration:

```env
NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8080
```
