import "./globals.css";

export const metadata = {
  title: "UK rent control policy dashboard | PolicyEngine",
  description:
    "Interactive dashboard estimating the fiscal and distributional effects of rent control policies in the UK.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
