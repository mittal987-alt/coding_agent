"use client";

import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { CheckCircle2, XCircle, Info, X } from "lucide-react";

type ToastType = "success" | "error" | "info";

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

interface ToastContextType {
  addToast: (type: ToastType, message: string, duration?: number) => void;
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
  info: (message: string, duration?: number) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((type: ToastType, message: string, duration = 3000) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, message, duration }]);
    if (duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, duration);
    }
  }, []);

  const success = useCallback((msg: string, dur?: number) => addToast("success", msg, dur), [addToast]);
  const error = useCallback((msg: string, dur?: number) => addToast("error", msg, dur), [addToast]);
  const info = useCallback((msg: string, dur?: number) => addToast("info", msg, dur), [addToast]);

  return (
    <ToastContext.Provider value={{ addToast, success, error, info }}>
      {children}
      <div className="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-lg shadow-xl border text-sm font-medium transform transition-all duration-300 translate-y-0 opacity-100 ${
              toast.type === "success"
                ? "bg-green-950/80 border-green-500/50 text-green-300"
                : toast.type === "error"
                ? "bg-red-950/80 border-red-500/50 text-red-300"
                : "bg-blue-950/80 border-blue-500/50 text-blue-300"
            }`}
            style={{ animation: "slideIn 0.3s ease-out forwards" }}
          >
            {toast.type === "success" && <CheckCircle2 size={16} className="text-green-400" />}
            {toast.type === "error" && <XCircle size={16} className="text-red-400" />}
            {toast.type === "info" && <Info size={16} className="text-blue-400" />}
            
            <p className="flex-1">{toast.message}</p>
            
            <button
              onClick={() => setToasts((prev) => prev.filter((t) => t.id !== toast.id))}
              className="p-1 hover:bg-white/10 rounded-md transition-colors"
            >
              <X size={14} className="opacity-70" />
            </button>
          </div>
        ))}
      </div>
      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </ToastContext.Provider>
  );
}
