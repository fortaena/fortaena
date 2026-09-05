import { describe, it, expect } from 'vitest';
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const root = join(__dirname, '..');

function readJson(rel: string) {
  return JSON.parse(readFileSync(join(root, rel), 'utf-8'));
}

describe('fortaena: project structure', () => {
  it('package.json exists with required scripts', () => {
    const pkg = readJson('package.json');
    expect(pkg.scripts.build).toBe('next build');
    expect(pkg.scripts['cf:build']).toBe('opennextjs-cloudflare build');
    expect(pkg.scripts['cf:deploy']).toBe('opennextjs-cloudflare deploy');
    expect(pkg.scripts.typecheck).toBe('tsc --noEmit');
    expect(pkg.scripts.lint).toBe('eslint .');
    expect(pkg.scripts.test).toBe('vitest run');
  });

  it('wrangler.jsonc has name fortaena', () => {
    const raw = readFileSync(join(root, 'wrangler.jsonc'), 'utf-8');
    const cleaned = raw.replace(/\/\/.*/g, '');
    expect(JSON.parse(cleaned).name).toBe('fortaena');
  });

  it('app/page.tsx exists and exports default function', () => {
    const code = readFileSync(join(root, 'app/page.tsx'), 'utf-8');
    expect(code).toContain('export default function Home');
    expect(code).toContain('Fortæana');
  });

  it('app/layout.tsx imports globals.css', () => {
    const code = readFileSync(join(root, 'app/layout.tsx'), 'utf-8');
    expect(code).toContain("import './globals.css'");
    expect(code).toContain('export const metadata');
  });

  it('next.config.mjs uses ESM export', () => {
    const code = readFileSync(join(root, 'next.config.mjs'), 'utf-8');
    expect(code).toContain('export default');
  });

  it('open-next.config.ts has no invalid properties', () => {
    const code = readFileSync(join(root, 'open-next.config.ts'), 'utf-8');
    expect(code).not.toContain('override');
    expect(code).toContain('defineCloudflareConfig');
  });

  it('.gitignore excludes build artifacts', () => {
    const gi = readFileSync(join(root, '.gitignore'), 'utf-8');
    expect(gi).toContain('.next/');
    expect(gi).toContain('.open-next/');
    expect(gi).toContain('node_modules/');
    expect(gi).toContain('.wrangler/');
  });

  it('no bun.lock or pnpm-lock in project', () => {
    expect(existsSync(join(root, 'bun.lock'))).toBe(false);
    expect(existsSync(join(root, 'pnpm-lock.yaml'))).toBe(false);
    expect(existsSync(join(root, 'package-lock.json'))).toBe(true);
  });

  it('package-lock.json exists and is valid', () => {
    const pkg = readJson('package-lock.json');
    expect(pkg.lockfileVersion).toBeGreaterThanOrEqual(2);
    expect(pkg.packages).toBeDefined();
  });
});
