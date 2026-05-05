"use client";

import { useState, useCallback } from "react";
import { Activity, Github } from "lucide-react";

import { DropZone } from "@/components/DropZone";
import { ProcessingStatus } from "@/components/ProcessingStatus";
import { FieldEditor } from "@/components/FieldEditor";
import { ExportPanel } from "@/components/ExportPanel";

import { uploadPdf } from "@/lib/api";
import { PatientData, ExtractionResult, AppStep } from "@/lib/types";

const emptyData = (): PatientData => ({
  nombre_paciente: null,
  documento: null,
  tipo_documento: null,
  edad: null,
  sexo: null,
  diagnostico_cie10: null,
  diagnostico_descripcion: null,
  tipo_cancer: null,
  estadificacion: null,
  fecha_diagnostico: null,
  tratamiento_inicial: null,
  resultado_tratamiento: null,
  medico_tratante: null,
});

export default function Home() {
  const [step, setStep] = useState<AppStep>("idle");
  const [processingStep, setProcessingStep] = useState(0);
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [patientData, setPatientData] = useState<PatientData>(emptyData());
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleFile = useCallback(async (file: File) => {
    setStep("processing");
    setErrorMsg(null);
    setProcessingStep(0);

    // Animate steps during upload
    const t1 = setTimeout(() => setProcessingStep(1), 1200);
    const t2 = setTimeout(() => setProcessingStep(2), 2600);

    try {
      const res = await uploadPdf(file);
      clearTimeout(t1);
      clearTimeout(t2);

      if (!res.success) {
        setErrorMsg(
          res.warnings.join(" ") || "No se pudo extraer información del PDF."
        );
        setStep("error");
        return;
      }

      setResult(res);
      setPatientData(res.data);
      setStep("editing");
    } catch (err: unknown) {
      clearTimeout(t1);
      clearTimeout(t2);
      const msg =
        err instanceof Error
          ? err.message
          : "Error de conexión. ¿Está el servidor corriendo?";
      setErrorMsg(msg);
      setStep("error");
    }
  }, []);

  const handleFieldChange = (field: keyof PatientData, value: string) => {
    setPatientData((prev) => ({ ...prev, [field]: value || null }));
  };

  const handleReset = () => {
    setStep("idle");
    setResult(null);
    setPatientData(emptyData());
    setErrorMsg(null);
    setProcessingStep(0);
  };

  return (
    <div className="flex min-h-screen flex-col">
      {/* ── Header ───────────────────────────────────────── */}
      <header className="glass sticky top-0 z-20 border-b border-white/60 px-6 py-4">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-500 shadow-sm">
              <Activity className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="text-base font-bold text-gray-900">DoctorCure</span>
              <span className="ml-2 text-xs text-gray-400">Historia Clínica → Excel</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <span className="hidden sm:block">100% local</span>
            <span className="inline-flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          </div>
        </div>
      </header>

      {/* ── Main ─────────────────────────────────────────── */}
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8 sm:px-6 lg:px-8">
        {/* Hero — only on idle/error */}
        {(step === "idle" || step === "error") && (
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">
              Extrae datos clínicos{" "}
              <span className="text-brand-500">automáticamente</span>
            </h1>
            <p className="mx-auto mt-3 max-w-xl text-base text-gray-500">
              Sube una historia clínica en PDF y obtén un Excel listo para usar.
              Procesamiento 100% local con OCR cuando el PDF es escaneado.
            </p>
          </div>
        )}

        {/* Panels */}
        <div
          className={`grid gap-6 ${
            step === "editing" ? "lg:grid-cols-[380px_1fr]" : "max-w-xl mx-auto"
          }`}
        >
          {/* Left panel */}
          <div className="space-y-4">
            {/* Upload card */}
            {(step === "idle" || step === "error") && (
              <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
                <h2 className="mb-4 text-sm font-semibold text-gray-700">
                  Subir Historia Clínica
                </h2>
                <DropZone onFile={handleFile} disabled={false} />

                {step === "error" && errorMsg && (
                  <div className="mt-4 rounded-xl bg-red-50 p-4 text-sm text-red-700 ring-1 ring-red-200">
                    <strong>Error:</strong> {errorMsg}
                  </div>
                )}
              </div>
            )}

            {/* Processing */}
            {step === "processing" && (
              <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
                <h2 className="mb-2 text-center text-sm font-semibold text-gray-700">
                  Procesando PDF…
                </h2>
                <ProcessingStatus step={processingStep} />
              </div>
            )}

            {/* Sidebar during editing: re-upload option */}
            {step === "editing" && (
              <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
                <h2 className="mb-4 text-sm font-semibold text-gray-700">
                  Subir otro PDF
                </h2>
                <DropZone onFile={handleFile} />
              </div>
            )}

            {/* Feature cards */}
            {step === "idle" && (
              <div className="grid grid-cols-3 gap-3">
                {[
                  { icon: "📄", title: "PDF Nativo", desc: "Texto digital directo" },
                  { icon: "🔍", title: "OCR local", desc: "PDFs escaneados" },
                  { icon: "📊", title: "Excel listo", desc: "Plantilla formateada" },
                ].map((f) => (
                  <div
                    key={f.title}
                    className="rounded-xl bg-white p-4 text-center shadow-sm ring-1 ring-gray-100"
                  >
                    <div className="mb-1 text-2xl">{f.icon}</div>
                    <p className="text-xs font-semibold text-gray-700">{f.title}</p>
                    <p className="text-[11px] text-gray-400">{f.desc}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right panel — editor */}
          {step === "editing" && result && (
            <div className="space-y-4">
              <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
                <div className="mb-4 flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-gray-700">
                    Revisar y editar datos
                  </h2>
                  <span className="text-xs text-gray-400">
                    Todos los campos son editables
                  </span>
                </div>
                <FieldEditor
                  data={patientData}
                  confidence={result.confidence}
                  warnings={result.warnings}
                  method={result.method}
                  onChange={handleFieldChange}
                />
              </div>

              <ExportPanel data={patientData} onReset={handleReset} />
            </div>
          )}
        </div>
      </main>

      {/* ── Footer ───────────────────────────────────────── */}
      <footer className="border-t border-gray-200 py-4 text-center text-xs text-gray-400">
        DoctorCure · Extracción local · Sin datos enviados a terceros
      </footer>
    </div>
  );
}
