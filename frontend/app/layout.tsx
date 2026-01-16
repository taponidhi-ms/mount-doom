import type { Metadata } from "next";
import { AntdRegistry } from '@ant-design/nextjs-registry';
import { TimezoneProvider } from '@/lib/timezone-context';

export const metadata: Metadata = {
  title: "Mount Doom - AI Agent Simulation",
  description: "Multi-agent conversation simulation and prompt generation platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <AntdRegistry>
          <TimezoneProvider>
            {children}
          </TimezoneProvider>
        </AntdRegistry>
      </body>
    </html>
  );
}
