import path from "node:path";

const nextConfig = {
  reactStrictMode: true,
  turbopack: {
    root: path.dirname(new URL(import.meta.url).pathname)
  }
};

export default nextConfig;
