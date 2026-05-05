export interface PatientData {
  nombre_paciente: string | null;
  documento: string | null;
  tipo_documento: string | null;
  edad: string | null;
  sexo: string | null;
  diagnostico_cie10: string | null;
  diagnostico_descripcion: string | null;
  tipo_cancer: string | null;
  estadificacion: string | null;
  fecha_diagnostico: string | null;
  tratamiento_inicial: string | null;
  resultado_tratamiento: string | null;
  medico_tratante: string | null;
}

export interface ExtractionResult {
  success: boolean;
  data: PatientData;
  raw_text: string;
  confidence: Record<string, number>;
  warnings: string[];
  method: string;
}

export interface FieldMeta {
  key: keyof PatientData;
  label: string;
  section: string;
  multiline?: boolean;
  placeholder?: string;
}

export const FIELD_DEFINITIONS: FieldMeta[] = [
  // ── Identificación ──────────────────────────────────────────
  { key: "nombre_paciente",      label: "Nombre del Paciente",      section: "Identificación del Paciente",  placeholder: "Apellido Nombre" },
  { key: "tipo_documento",       label: "Tipo de Documento",        section: "Identificación del Paciente",  placeholder: "Cédula de Ciudadanía" },
  { key: "documento",            label: "Número de Documento",      section: "Identificación del Paciente",  placeholder: "12345678" },
  { key: "edad",                 label: "Edad",                     section: "Identificación del Paciente",  placeholder: "45" },
  { key: "sexo",                 label: "Sexo",                     section: "Identificación del Paciente",  placeholder: "Masculino / Femenino" },
  // ── Diagnóstico ─────────────────────────────────────────────
  { key: "diagnostico_cie10",    label: "Código CIE-10",            section: "Diagnóstico Oncológico",       placeholder: "C50.1" },
  { key: "diagnostico_descripcion", label: "Descripción Diagnóstico", section: "Diagnóstico Oncológico",    placeholder: "Descripción del diagnóstico", multiline: true },
  { key: "tipo_cancer",          label: "Tipo de Cáncer",           section: "Diagnóstico Oncológico",       placeholder: "Cáncer de mama" },
  { key: "estadificacion",       label: "Estadificación",           section: "Diagnóstico Oncológico",       placeholder: "IIA / T2N1M0" },
  { key: "fecha_diagnostico",    label: "Fecha de Diagnóstico",     section: "Diagnóstico Oncológico",       placeholder: "DD/MM/AAAA" },
  // ── Tratamiento ─────────────────────────────────────────────
  { key: "tratamiento_inicial",  label: "Tratamiento Inicial",      section: "Tratamiento",                  placeholder: "Quimioterapia + Cirugía", multiline: true },
  { key: "resultado_tratamiento",label: "Resultado del Tratamiento",section: "Tratamiento",                  placeholder: "Remisión completa", multiline: true },
  // ── Equipo médico ───────────────────────────────────────────
  { key: "medico_tratante",      label: "Médico Tratante",          section: "Equipo Médico",                placeholder: "Dr. Nombre Apellido" },
];

export type AppStep = "idle" | "processing" | "editing" | "error";
