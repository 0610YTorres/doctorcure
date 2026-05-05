import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DoctorCure — Historia Clínica a Excel",
  description: "Extracción automática de historias clínicas en PDF hacia Excel",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
        {children}
      </body>
    </html>
  );
}
