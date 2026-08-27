import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ShikshaFlow",
  description: "Intelligent Lesson Planner & Teacher Workspace",
  manifest: "/manifest.json",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <meta name="theme-color" content="#4F46E5" />
        <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
      </head>
      <body className="antialiased min-h-screen flex flex-col bg-background text-foreground">
        {children}
      </body>
    </html>
  );
}
