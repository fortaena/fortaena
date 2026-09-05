// Fortæana - UAP Investigative Archive Platform
// Mission: Disruptive investigative journalism + NeoEngineering Data Science
// Tech: Next.js 16 + OpenNext Cloudflare + TypeScript

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/app/globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Fortæana | UAP Investigative Archive',
  description: 'Game-changer platform for Disruptive Investigative Journalism & NeoEngineering Data Science - Open-source UAP archive (CC0)',
  metadataBase: new URL('https://fortaena.edu-pretended104.workers.dev'),
  openGraph: {
    title: 'Fortæana | UAP Investigative Archive',
    description: 'Advanced platform for investigative journalism and data science',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
