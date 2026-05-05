"use client";

import { useState } from "react";
import { FileSpreadsheet, Download, RotateCcw, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PatientData } from "@/lib/types";
import { exportExcel } from "@/lib/api";

interface ExportPanelProps {
  data: PatientData;
  onReset: () => void;
}

export function ExportPanel({ data, onReset }: ExportPanelProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  const handleExport = async () => {
    setLoading(true);
    setError(null);
    try {
      const name = data.nombre_paciente?.replace(/\s+/g, "_") ?? "paciente";
      await exportExcel(data, `historia_clinica_${name}.xlsx`);
      setDone(true);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error al exportar");
    } finally {
      setLoading(false);
    }
  };

  const filled = Object.values(data).filter(Boolean).length;
  const total = Object.keys(data).length;

  return (
    <div className="sticky bottom-0 z-10 rounded-2xl bg-white p-5 shadow-xl ring-1 ring-gray-200">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50">
            <FileSpreadsheet className="h-5 w-5 text-brand-600" />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-800">Listo para exportar</p>
            <p className="text-xs text-gray-500">
              {filled} de {total} campos completados
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" size="md" onClick={onReset}>
            <RotateCcw className="h-4 w-4" />
            Nuevo PDF
          </Button>
          <Button
            size="md"
            variant="success"
            onClick={handleExport}
            disabled={loading}
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Download className="h-4 w-4" />
            )}
            {done ? "Descargar de nuevo" : "Exportar Excel"}
          </Button>
        </div>
      </div>

      {error && (
        <p className="mt-3 text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2">{error}</p>
      )}

      {done && !error && (
        <p className="mt-3 text-xs text-emerald-700 bg-emerald-50 rounded-lg px-3 py-2">
          ✓ Archivo descargado correctamente
        </p>
      )}
    </div>
  );
}
