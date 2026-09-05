export default function ReportsPage() {
  return (
    <section>
      <h1>Reportes técnicos</h1>
      <p>Incidentes y logs de desarrollo documentados en Obsidian.</p>

      <article className="card">
        <h2>2026-09-04 — Build Incident</h2>
        <p>El deploy a Cloudflare falló repetidamente por:</p>
        <ul>
          <li>error TS2353: <code>override</code> no existe en CloudflareOverrides</li>
          <li>module is not defined en ES module scope (postcss.config.js con "type": "module")</li>
          <li>tailwindcss-animate not found</li>
          <li>Error recursivo en opennextjs-cloudflare build al ejecutar <code>npm run build</code></li>
        </ul>
        <p><strong>Resolución:</strong> Eliminar <code>override</code>, renombrar postcss.config.js a .cjs, asegurar "build" apunte a "next build", no a opennextjs.</p>
      </article>

      <article className="card">
        <h2>Scrapers T6 — Estado de fuentes</h2>
        <table>
          <tr><th>Fuente</th><th>Estado</th><th>Método</th></tr>
          <tr><td>AARO</td><td>✅ 5 PDFs extraídos</td><td>Jina AI → tabla markdown</td></tr>
          <tr><td>EOC</td><td>✅ 2/3 artículos</td><td>httpx + BeautifulSoup</td></tr>
          <tr><td>CIA FOIA</td><td>⚠️ Búsqueda vacía</td><td>Jina AI; requiere JS rendering</td></tr>
          <tr><td>GEIPAN</td><td>🔴 429 rate-limited</td><td>Tanto Jina como HTTP directo</td></tr>
          <tr><td>NUFORC</td><td>🔴 403 Cloudflare</td><td>Requiere headless/playwright</td></tr>
          <tr><td>FBI Vault</td><td>🔴 403</td><td>Protección anti-bot</td></tr>
          <tr><td>OpenSky</td><td>🔴 403</td><td>Requiere API key</td></tr>
        </table>
      </article>

      <article className="card">
        <h2>Auditoría final</h2>
        <ul>
          <li>Typecheck: 0 errores</li>
          <li>Build: SSG generado (3 páginas estáticas)</li>
          <li>Tests: 9/9 passing</li>
          <li>Lint: 0 errores</li>
          <li>OpenNext build: worker.js generado</li>
          <li>Deploy: Cloudflare Workers — HTTP 200, headers x-opennext: 1</li>
        </ul>
      </article>
    </section>
  );
}
