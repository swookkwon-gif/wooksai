import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  basePath: "/wooksai",
  images: { unoptimized: true },
};

export default nextConfig;
