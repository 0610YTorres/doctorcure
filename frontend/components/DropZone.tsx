"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, X, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface DropZoneProps {
  onFile: (file: File) => void;
  disabled?: boolean;
}

export function DropZone({ onFile, disabled }: DropZoneProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [sizeError, setSizeError] = useState(false);

  const onDrop = useCallback(
    (accepted: File[]) => {
      setSizeError(false);
      const file = accepted[0];
      if (!file) return;
      if (file.size > 20 * 1024 * 1024) {
        setSizeError(true);
        return;
      }
      setSelectedFile(file);
    },
    []
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    disabled,
  });

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedFile(null);
    setSizeError(false);
  };

  const handleAnalyze = () => {
    if (selectedFile) onFile(selectedFile);
  };

  return (
    <div className="w-full space-y-4">
      <div
        {...getRootProps()}
        className={cn(
          "relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 text-center transition-all cursor-pointer",
          isDragActive
            ? "border-brand-500 bg-brand-50 scale-[1.01]"
            : selectedFile
            ? "border-emerald-400 bg-emerald-50"
            : "border-gray-300 bg-gray-50 hover:border-brand-400 hover:bg-brand-50",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      >
        <input {...getInputProps()} />

        {selectedFile ? (
          <>
            <div className="mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-100">
              <FileText className="h-7 w-7 text-emerald-600" />
            </div>
            <p className="font-semibold text-gray-800">{selectedFile.name}</p>
            <p className="mt-1 text-sm text-gray-500">
              {(selectedFile.size / 1024).toFixed(0)} KB
            </p>
            <button
              onClick={handleClear}
              className="absolute right-3 top-3 rounded-full p-1 text-gray-400 hover:bg-gray-200 hover:text-gray-600"
            >
              <X className="h-4 w-4" />
            </button>
          </>
        ) : (
          <>
            <div
              className={cn(
                "mb-4 flex h-16 w-16 items-center justify-center rounded-full transition-colors",
                isDragActive ? "bg-brand-100" : "bg-gray-200"
              )}
            >
              <Upload
                className={cn(
                  "h-8 w-8 transition-colors",
                  isDragActive ? "text-brand-600" : "text-gray-400"
                )}
              />
            </div>
            <p className="text-base font-semibold text-gray-700">
              {isDragActive ? "Suelta el PDF aquí" : "Arrastra tu historia clínica"}
            </p>
            <p className="mt-1 text-sm text-gray-500">
              o <span className="text-brand-600 font-medium">haz clic para seleccionar</span>
            </p>
            <p className="mt-3 text-xs text-gray-400">PDF · Máximo 20 MB</p>
          </>
        )}
      </div>

      {sizeError && (
        <div className="flex items-center gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 shrink-0" />
          El archivo supera el límite de 20 MB.
        </div>
      )}

      {selectedFile && (
        <Button
          onClick={handleAnalyze}
          disabled={disabled}
          size="lg"
          className="w-full"
        >
          <FileText className="h-5 w-5" />
          Analizar Historia Clínica
        </Button>
      )}
    </div>
  );
}
