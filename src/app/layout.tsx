import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KnowledgeAI - AI Personal Knowledge Assistant",
  description: "Multi-agent system for organizing, retrieving, and synthesizing information with AI.",
  openGraph: {
    title: "KnowledgeAI - AI Personal Knowledge Assistant",
    description: "Multi-agent system for organizing, retrieving, and synthesizing information with AI.",
    url: "https://knowledge-assistant-rho.vercel.app",
    images: [{ url: "https://raw.githubusercontent.com/PremJibon/kaggle_submit/main/thumbnail.svg", width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: "KnowledgeAI - AI Personal Knowledge Assistant",
    description: "Multi-agent system for organizing, retrieving, and synthesizing information with AI.",
    images: ["https://raw.githubusercontent.com/PremJibon/kaggle_submit/main/thumbnail.svg"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}