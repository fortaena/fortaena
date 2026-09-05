import Link from "next/link";

export default function Home() {
  return (
    <section>
      <h1>Fortæana</h1>
      <p>Archivo de avistamientos OVI/UAP.</p>
      <p>
        Proyecto CC0: ingesta automatizada desde fuentes gubernamentales,
        académicas y ciudadanas. Sin muros de pago. Sin censura.
        Datos públicos, accesibles y verificables.
      </p>
      <ul>
        <li><Link href="/fuentes">Fuentes gubernamentales e institucionales</Link></li>
        <li><Link href="/guia">Guía de build/deploy y checklist</Link></li>
        <li><Link href="/reports">Reportes técnicos</Link></li>
      </ul>
    </section>
  );
}
