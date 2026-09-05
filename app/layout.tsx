import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Fortæana — Archivo de avistamientos OVI/UAP",
  description: "Archivo público de avistamientos OVI/UAP. Fuentes gubernamentales, ingestas estructuradas y datos abiertos.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className={inter.className}>
        <nav className="nav">
          <a href="/">Inicio</a>
          <a href="/fuentes">Fuentes</a>
          <a href="/guia">Guía</a>
          <a href="/reports">Reports</a>
        </nav>
        <main>{children}</main>
        <footer>Fortæana · CC0 · Datos públicos</footer>
      </body>
    </html>
  );
}
