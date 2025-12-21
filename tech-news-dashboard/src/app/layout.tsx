import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: 'swap',
  weight: ['300', '400', '500', '600', '700'],
});

export const metadata: Metadata = {
  title: "TechNews Dashboard - Your Personal Tech News Aggregator",
  description: "Stay updated with the latest technology news from top sources. AI-powered categorization and relevance scoring.",
  keywords: ["tech news", "technology", "AI", "programming", "development", "news aggregator"],
  authors: [{ name: "TechNews Dashboard" }],
  openGraph: {
    title: "TechNews Dashboard",
    description: "Your personal tech news aggregator with AI-powered insights",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "TechNews Dashboard",
    description: "Stay updated with the latest technology news",
  },
  robots: {
    index: false,
    follow: false,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} antialiased`}>
        {children}
      </body>
    </html>
  );
}