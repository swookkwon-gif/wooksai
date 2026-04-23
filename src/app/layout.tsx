import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });

export const metadata: Metadata = {
  title: "Wook's AI and Marketing",
  description: "AI와 디지털 마케팅의 실무적인 인사이트, 트렌드, 그리고 커리어를 다루는 블로그입니다.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className={`${inter.variable} ${outfit.variable}`}>
      <body className="antialiased overflow-x-hidden">
        <div className="fixed top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-[400px] hero-glow -z-10 opacity-50" />
        {children}
      </body>
    </html>
  );
}
