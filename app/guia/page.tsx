export default function GuiaPage() {
  const fases = [
    {t:"Fase 1: Validación Local",items:["git status → sin .DS_Store, node_modules, LustermordVault/, .next/, .open-next/, .wrangler/","ls bun.lock → NO existe (Cloudflare necesita package-lock.json)","ls package-lock.json → EXISTE",'grep "type" package.json → "type": "module" O ausente, nunca "commonjs"',"cat open-next.config.ts → SIN propiedad override","ls postcss.config.cjs → EXISTE (no .js con type: module)"]},
    {t:"Fase 2: Build",items:["npm run build → 0 errors, 0 warnings de PostCSS/Tailwind","ls .open-next/worker.js → EXISTE tras build","ls .open-next/assets/ → archivos estáticos generados",".open-next/ → no está en .gitignore (pero SÍ en .next/)"]},
    {t:"Fase 3: Token Cloudflare",items:["Dashboard → Settings → Builds → API token → NO es el revocado","Dashboard → Variables → CLOUDFLARE_API_TOKEN → coincide con Build token","Token tiene scope: Workers Edit + Account Account Settings","Si hay duda: CLOUDFLARE_API_TOKEN=xxx npx wrangler whoami"]},
    {t:"Fase 4: Push + Deploy",items:['git add -A && git commit -m "description"',"git push origin main → Cloudflare detecta webhook",'Esperar build en Dashboard → verificar "Success"',"Si falla: CLOUDFLARE_API_TOKEN=xxx npx wrangler deploy (manual)"]},
    {t:"Fase 5: Verificación Post-Deploy",items:["curl -sI URL → STATUS 200","Headers incluyen x-opennext: 1","Abrir en navegador → contenido visible",'Verificar title contiene "Fortæana"',"Si todo OK: commitar el log de build en Obsidian"]}
  ];
  const errores=[["Unknown lockfile version","rm bun.lock && npm install"],["Infinite opennextjs build","build → next build en package.json"],["module is not defined","Renombrar postcss.config.js → .cjs"],["tailwindcss-animate not found","npm install tailwindcss-animate"],["TS2353: override","Eliminar override de open-next.config.ts"],["Token revocado","Crear nuevo en Dashboard; actualizar AMBOS"],["@tailwindcss/postcss not found","npm install @tailwindcss/postcss"]];
  return (<section><h1>Guía de build / deploy Fortæana</h1><p>Checklist obligatorio antes de cada deploy.</p>
    {fases.map(f=>(<div key={f.t}><h2>{f.t}</h2><ul>{f.items.map(i=><li key={i}>{i}</li>)}</ul></div>))}
    <h2>Errores Comunes y Fix Rápido</h2><table><thead><tr><th>Error</th><th>Fix</th></tr></thead><tbody>
      {errores.map(([e,f])=><tr key={e}><td>{e}</td><td>{f}</td></tr>)}</tbody></table></section>);
}
