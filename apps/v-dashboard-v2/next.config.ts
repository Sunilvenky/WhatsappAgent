import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  async rewrites() {
    return [
      {
        source: '/gateway/:path*',
        destination: 'http://129.159.224.220:3001/:path*',
      },
      {
        source: '/backend/:path*',
        destination: 'http://129.159.224.220:3000/api/v1/:path*',
      },
    ];
  },
};

export default nextConfig;
