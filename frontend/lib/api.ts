import axios from "axios";
import { ExtractionResult, PatientData } from "./types";

// En producción (desktop/servidor): NEXT_PUBLIC_API_URL="" → BASE="" → URLs relativas
// En desarrollo (npm run dev):      NEXT_PUBLIC_API_URL no definida → http://localhost:8000
// IMPORTANTE: usar ?? no || porque || trata "" como falso
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const client = axios.create({ baseURL: BASE, timeout: 60_000 });

export async function uploadPdf(file: File): Promise<ExtractionResult> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await client.post<ExtractionResult>("/api/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function exportExcel(patientData: PatientData, filename?: string): Promise<void> {
  const { data } = await client.post(
    "/api/export",
    { data: patientData, filename },
    { responseType: "blob" }
  );

  const url = URL.createObjectURL(new Blob([data]));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename ?? `historia_clinica_${Date.now()}.xlsx`;
  a.click();
  URL.revokeObjectURL(url);
}
