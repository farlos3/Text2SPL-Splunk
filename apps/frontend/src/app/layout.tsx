import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SPL Assistant - KBTG Cybersecurity AI",
  description: "AI-powered assistant for Splunk SPL queries and cybersecurity analysis. Get expert help with data modeling, threat hunting, and log analysis.",
  keywords: ["SPL", "Splunk", "AI", "Cybersecurity", "KBTG", "Assistant", "Threat Hunting", "SIEM"],
  authors: [{ name: "KBTG Cyber Security Team" }],
  viewport: "width=device-width, initial-scale=1",
  themeColor: "#3b82f6",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <meta name="theme-color" content="#3b82f6" />
      </head>
      <body className="antialiased font-sans bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-blue-950 min-h-screen">
        <div id="root" className="relative">
          {children}
        </div>
      </body>
    </html>
  );
}
