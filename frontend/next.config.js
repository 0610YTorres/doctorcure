/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Exportación estática: genera la carpeta "out/" lista para servir sin Node.js
  output: "export",
  images: { unoptimized: true },
  // Necesario para que los assets funcionen desde FastAPI
  trailingSlash: false,
};

module.exports = nextConfig;
