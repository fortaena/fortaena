export default function FuentesPage() {
  return (
    <section>
      <h1>Fuentes gubernamentales / institucionales</h1>
      <p>Fuentes verificadas, de acceso gratuito, sin tarjeta de crédito. Todas CC0 o Public Domain.</p>

      <h2>1. Estados Unidos</h2>

      <h3>Departamento de Defensa</h3>
      <ul>
        <li><strong>AARO</strong> — aaro.mil — Informes anuales, hearings, seguridad nacional</li>
        <li><strong>AARO FOIA Reading Room</strong> — aaro.mil/foia/reading-room — Documentos desclasificados</li>
        <li><strong>DoD UAP Releases</strong> — defense.gov/News/Releases — Videos oficiales (FLIR1, Gimbal, GoFast)</li>
        <li><strong>War Department Records</strong> — archives.gov/research/military — Registros históricos WWII+</li>
      </ul>

      <h3>FBI</h3>
      <ul>
        <li><strong>FBI Vault — UFO</strong> — vault.fbi.gov/UFO — Investigaciones sobre avistamientos</li>
        <li><strong>FBI Vault — Unexplained Phenomena</strong> — vault.fbi.gov — Documentos internos desclasificados</li>
      </ul>

      <h3>NASA</h3>
      <ul>
        <li><strong>NASA UAP Independent Study Team</strong> — science.nasa.gov/uap — Informe final 2023</li>
        <li><strong>NASA FOIA Library</strong> — nasa.gov/foia — Documentos solicitados via FOIA</li>
        <li><strong>NASA NTRS</strong> — ntrs.nasa.gov — Papers tecnicos UAP</li>
        <li><strong>NASA FIRMS</strong> — firms.modaps.eosdis.nasa.gov — Anomalias termicas satelitales</li>
      </ul>

      <h3>CIA</h3>
      <ul>
        <li><strong>CIA CREST</strong> — cia.gov/readingroom — Documentos desclasificados</li>
        <li><strong>CIA FOIA — UFO Collection</strong> — cia.gov/readingroom/collection/ufos — Coleccion especifica UAP</li>
      </ul>

      <h3>Otras agencias EE.UU.</h3>
      <ul>
        <li><strong>NTSB</strong> — ntsb.gov/Pages/AviationQuery.aspx — Incidentes aviacion</li>
        <li><strong>NOAA / NCEI</strong> — ncei.noaa.gov — Datos meteorologicos para correlacion</li>
      </ul>

      <h2>2. Internacionales</h2>

      <h3>Francia</h3>
      <ul>
        <li><strong>CNES GEIPAN</strong> — cnes-geipan.fr/en — Base de datos GEIPAN</li>
      </ul>

      <h3>Reino Unido</h3>
      <ul>
        <li><strong>UK MOD — UFO Files</strong> — nationalarchives.gov.uk/ufos — Archivos 1950-2009</li>
      </ul>

      <h3>Brasil</h3>
      <ul>
        <li><strong>DECEA</strong> — gov.br/decea — Reportes brasileños</li>
      </ul>

      <h3>Chile</h3>
      <ul>
        <li><strong>CEFAA</strong> — cefaa.cl — Investigacion gubernamental activa</li>
      </ul>

      <h3>Australia</h3>
      <ul>
        <li><strong>RAAF / National Archives</strong> — archives.gov.au — Archivos historicos australianos</li>
      </ul>

      <h2>3. Redes academicas / cientificas</h2>
      <ul>
        <li><strong>Harvard Galileo Project</strong> — projects.iq.harvard.edu/galileo/home</li>
        <li><strong>MUFON</strong> — mufon.com — Base de datos 100k+ casos</li>
        <li><strong>NUFORC</strong> — nuforc.org/databank — Reportes ciudadanos</li>
        <li><strong>CUFOS</strong> — cufos.org</li>
        <li><strong>SCU</strong> — scufos.org — Papers cientificos</li>
        <li><strong>OpenSky Network</strong> — opensky-network.org — Radar civil abierto</li>
      </ul>

      <h2>4. Notas de acceso</h2>
      <ul>
        <li>FOIA requests: foia.gov</li>
        <li>NARA: archives.gov</li>
        <li>GEIPAN API: registro gratuito para API completa</li>
        <li>OpenSky: key gratuita; rate limit 10 req/seg</li>
        <li>FIRMS: key gratuita; data con retraso 3h</li>
      </ul>

      <h2>5. Prioridad de integracion</h2>
      <ol>
        <li>NUFORC</li>
        <li>El Ojo Critico</li>
        <li>AARO + FBI Vault</li>
        <li>CNES GEIPAN</li>
        <li>NASA FIRMS</li>
        <li>OpenSky</li>
        <li>UK MOD Archives</li>
        <li>CIA CREST</li>
        <li>Resto internacionales</li>
      </ol>
    </section>
  );
}
