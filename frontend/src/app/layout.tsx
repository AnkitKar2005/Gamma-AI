import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Providers from "./providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Gamma AI — Intelligent Operating System",
  description:
    "Multi-agent AI operating system with real-time streaming, voice I/O, persistent memory, and proactive intelligence.",
  keywords: ["AI", "Assistant", "Multi-Agent", "Voice", "Real-time"],
  authors: [{ name: "Gamma AI" }],
  openGraph: {
    title: "Gamma AI",
    description: "Your intelligent AI operating system",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
