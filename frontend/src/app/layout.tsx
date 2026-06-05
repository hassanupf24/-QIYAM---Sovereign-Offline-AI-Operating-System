import type { Metadata } from "next";
import { Cairo } from "next/font/google";
import "./globals.css";

const cairo = Cairo({ subsets: ["arabic"], display: "swap" });

export const metadata: Metadata = {
  title: "QIYAM AI | Sovereign Operating System",
  description: "Enterprise Multi-Agent Intelligence Dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ar" dir="rtl">
      <body className={`bg-background text-white min-h-screen flex overflow-hidden ${cairo.className}`}>
        {children}
      </body>
    </html>
  );
}
