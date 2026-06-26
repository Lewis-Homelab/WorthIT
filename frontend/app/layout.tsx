import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WorthIT — worth your weekend",
  description:
    "Browse ranked day experiences by joy per pound — not just nearby pins.",
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
