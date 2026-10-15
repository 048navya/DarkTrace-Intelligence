import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DarkTrace Intelligence",
  description: "An evidence-led investigation workspace by GENZ CODERS-1.",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
