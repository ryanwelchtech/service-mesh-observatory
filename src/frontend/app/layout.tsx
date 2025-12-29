import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Service Mesh Observatory',
  description: 'Comprehensive observability and security platform for Istio and Linkerd service mesh deployments',
  keywords: ['Kubernetes', 'Istio', 'Service Mesh', 'Observability', 'DevSecOps', 'Cloud Security'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
