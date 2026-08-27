import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Force Next.js to use the correct workspace root and avoid parent lockfile issues
  outputFileTracingRoot: path.join(__dirname),
};

export default nextConfig;
