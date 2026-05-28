import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Backend API proxy to avoid CORS in development
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8080/api/:path*",
      },
      {
        source: "/ws/:path*",
        destination: "http://localhost:8080/ws/:path*",
      },
    ];
  },
};

export default nextConfig;
