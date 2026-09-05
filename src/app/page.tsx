// Fortæana Home Page - Disruptive Investigative Journalism & NeoEngineering Data Science
import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-900 text-gray-100 py-16 px-4 sm:px-6 lg:px-8 flex flex-col items-center">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
          Fortæana
        </h1>
        <p className="text-xl text-gray-300 max-w-2xl">
          Zero-cost UAP Archive Platform - Advanced investigative journalism & NeoEngineering Data Science
        </p>
        <a href="https://fortaena.edu-pretended104.workers.dev" className="inline-block mt-6 bg-blue-500 hover:bg-blue-600 text-white font-medium px-6 py-3 rounded-md transition-colors">
          Live Platform →
        </a>
      </header>

      <section className="w-full max-w-4xl space-y-12">
        <div className="space-y-6">
          <h2 className="text-2xl font-semibold">Disruptive Investigative Journalism</h2>
          <p className="text-gray-300">
            Pioneering platform for investigative reporting on UAP/OVNI phenomena, combining rigorous
            journalism with open-source intelligence gathering and collaborative verification.
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Structured UAP report ingestion & normalization</li>
            <li>Source verification & credibility scoring</li>
            <li>Collaborative investigation workflows</li>
            <li>Public interest journalism with CC0 licensing</li>
          </ul>
        </div>

        <div className="space-y-6">
          <h2 className="text-2xl font-semibold">NeoEngineering Data Science</h2>
          <p className="text-gray-300">
            Advanced data science & engineering pipeline for UAP data analysis, pattern recognition,
            and anomaly detection using modern ML/AI techniques.
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Multi-modal data fusion (reports, sensor data, imagery)</li>
            <li>Statistical anomaly detection & clustering</li>
            <li>Knowledge graph construction (Neo4j backend)</li>
            <li>Reproducible research & open datasets</li>
          </ul>
        </div>

        <div className="space-y-6">
          <h2 className="text-2xl font-semibold">Technical Architecture</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold mb-2">Frontend</h3>
              <ul className="text-sm text-gray-300 list-disc list-inside space-y-1">
                <li>Next.js 16 (App Router)</li>
                <li>React 19 + TypeScript</li>
                <li>OpenNext Cloudflare Workers</li>
                <li>Tailwind CSS (via globals.css)</li>
              </ul>
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold mb-2">Backend & Data</h3>
              <ul className="text-sm text-gray-300 list-disc list-inside space-y-1">
                <li>Python ingestion pipeline</li>
                <li>Neo4j graph database</li>
                <li>IPFS decentralized storage</li>
                <li>Cloudflare Pages/Workers</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <h2 className="text-2xl font-semibold">Get Involved</h2>
          <p className="text-gray-300">
            Fortæana is built on open collaboration. Contribute to the mission:
          </p>
          <div className="flex flex-col space-y-3 mt-4">
            <a href="https://github.com/fortaena/fortaena" className="bg-gray-700 hover:bg-gray-600 text-white font-medium px-4 py-2 rounded-md transition-colors">
              GitHub Repository (CC0)
            </a>
            <a href="https://fortaena.edu-pretended104.workers.dev" className="bg-gray-700 hover:bg-gray-600 text-white font-medium px-4 py-2 rounded-md transition-colors">
              Explore Live Archive
            </a>
          </div>
        </div>
      </section>

      <footer className="mt-auto pt-8 text-center text-xs text-gray-400 border-t border-gray-700">
        © 2026 Fortæana - CC0 License • Built with Hermes Agent (GLM 5.2 Ultra-Reasoning)
      </footer>
    </main>
  );
}