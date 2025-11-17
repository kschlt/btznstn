import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Betzenstein Buchung",
  description: "Buchungssystem für Betzenstein",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="de">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  )
}
