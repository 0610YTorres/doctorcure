"use client";

import { Loader2, Brain, FileSearch, FileSpreadsheet } from "lucide-react";

const STEPS = [
  { icon: FileSearch,       label: "Leyendo PDF",               desc: "Extrayendo texto con pdfplumber / PyMuPDF" },
  { icon: Brain,            label: "Analizando campos",          desc: "Aplicando patrones de extracción médica" },
  { icon: FileSpreadsheet,  label: "Preparando datos",           desc: "Mapeando campos al formato Excel" },
];

interface ProcessingStatusProps {
  step?: number;
}

export function ProcessingStatus({ step = 0 }: ProcessingStatusProps) {
  return (
    <div className="flex flex-col items-center space-y-8 py-8">
      <div className="relative flex h-20 w-20 items-center justify-center">
        <div className="absolute inset-0 rounded-full border-4 border-brand-100" />
        <div className="absolute inset-0 animate-spin rounded-full border-4 border-transparent border-t-brand-500" />
        <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
      </div>

      <div className="w-full max-w-sm space-y-3">
        {STEPS.map((s, i) => {
          const Icon = s.icon;
          const isActive = i === step;
          const isDone = i < step;
          return (
            <div
              key={i}
              className={`flex items-start gap-3 rounded-xl p-3 transition-all ${
                isActive ? "bg-brand-50 ring-1 ring-brand-200" : isDone ? "opacity-60" : "opacity-30"
              }`}
            >
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                  isDone
                    ? "bg-emerald-100 text-emerald-600"
                    : isActive
                    ? "bg-brand-100 text-brand-600"
                    : "bg-gray-100 text-gray-400"
                }`}
              >
                <Icon className="h-4 w-4" />
              </div>
              <div>
                <p className={`text-sm font-semibold ${isActive ? "text-brand-700" : "text-gray-600"}`}>
                  {s.label}
                </p>
                <p className="text-xs text-gray-400">{s.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
