import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "vibe_home",
  description: "Frontend foundation for vibe_home.",
};

type RootLayoutProps = {
  children: React.ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
