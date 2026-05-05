"use client";

import { PatientData, FIELD_DEFINITIONS, FieldMeta } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { CheckCircle2, AlertCircle } from "lucide-react";

interface FieldEditorProps {
  data: PatientData;
  confidence: Record<string, number>;
  warnings: string[];
  method: string;
  onChange: (field: keyof PatientData, value: string) => void;
}

export function FieldEditor({ data, confidence, warnings, method, onChange }: FieldEditorProps) {
  const sections = Array.from(new Set(FIELD_DEFINITIONS.map((f) => f.section)));

  const methodLabel: Record<string, string> = {
    pdfplumber: "pdfplumber",
    pymupdf: "PyMuPDF",
    ocr_tesseract: "OCR Tesseract",
    ocr_failed: "Sin OCR",
  };

  return (
    <div className="space-y-6">
      {/* Top bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-emerald-50 px-4 py-3 ring-1 ring-emerald-200">
        <div className="flex items-center gap-2 text-sm font-semibold text-emerald-700">
          <CheckCircle2 className="h-4 w-4" />
          Extracción completa
        </div>
        <Badge variant="info">Motor: {methodLabel[method] ?? method}</Badge>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="rounded-xl bg-amber-50 p-4 ring-1 ring-amber-200">
          <div className="flex items-center gap-2 text-sm font-semibold text-amber-700 mb-2">
            <AlertCircle className="h-4 w-4" />
            Avisos
          </div>
          <ul className="space-y-1">
            {warnings.map((w, i) => (
              <li key={i} className="text-xs text-amber-600 flex items-start gap-1.5">
                <span className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
                {w}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Sections */}
      {sections.map((section) => {
        const fields = FIELD_DEFINITIONS.filter((f) => f.section === section);
        return (
          <div key={section} className="overflow-hidden rounded-xl ring-1 ring-gray-200">
            <div className="bg-gray-50 px-4 py-2.5">
              <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500">
                {section}
              </h3>
            </div>
            <div className="divide-y divide-gray-100">
              {fields.map((field) => (
                <FieldRow
                  key={field.key}
                  field={field}
                  value={data[field.key] ?? ""}
                  confidence={confidence[field.key] ?? 0}
                  onChange={(v) => onChange(field.key, v)}
                />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

interface FieldRowProps {
  field: FieldMeta;
  value: string;
  confidence: number;
  onChange: (v: string) => void;
}

function FieldRow({ field, value, confidence, onChange }: FieldRowProps) {
  const hasValue = value.trim().length > 0;
  const confColor =
    confidence >= 0.8
      ? "bg-emerald-400"
      : confidence >= 0.5
      ? "bg-amber-400"
      : confidence > 0
      ? "bg-orange-400"
      : "bg-gray-200";

  const inputClass = cn(
    "w-full rounded-lg border px-3 py-2 text-sm text-gray-800 outline-none transition-all",
    "focus:ring-2 focus:ring-brand-500 focus:border-brand-500",
    hasValue ? "border-gray-200 bg-white" : "border-dashed border-gray-300 bg-gray-50"
  );

  return (
    <div className="grid grid-cols-[180px_1fr_8px] items-start gap-3 px-4 py-3">
      <div className="flex flex-col justify-center">
        <span className="text-xs font-semibold text-gray-600">{field.label}</span>
        {confidence > 0 && (
          <div className="mt-1 flex items-center gap-1.5">
            <div className="h-1.5 w-16 overflow-hidden rounded-full bg-gray-100">
              <div
                className={cn("h-full rounded-full transition-all", confColor)}
                style={{ width: `${Math.round(confidence * 100)}%` }}
              />
            </div>
            <span className="text-[10px] text-gray-400">{Math.round(confidence * 100)}%</span>
          </div>
        )}
      </div>

      {field.multiline ? (
        <textarea
          className={cn(inputClass, "min-h-[64px] resize-y")}
          value={value}
          placeholder={field.placeholder}
          onChange={(e) => onChange(e.target.value)}
          rows={2}
        />
      ) : (
        <input
          type="text"
          className={inputClass}
          value={value}
          placeholder={field.placeholder}
          onChange={(e) => onChange(e.target.value)}
        />
      )}

      <div className={cn("mt-2.5 h-2 w-2 rounded-full shrink-0", hasValue ? "bg-emerald-400" : "bg-gray-200")} />
    </div>
  );
}
