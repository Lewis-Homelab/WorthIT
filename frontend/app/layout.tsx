import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WorthIT",
  description: "High-value experience planning — joy per pound",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
