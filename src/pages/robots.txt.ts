export const prerender = true;

const site =
  import.meta.env.PUBLIC_SITE_URL ||
  (import.meta.env.VERCEL_URL ? `https://${import.meta.env.VERCEL_URL}` : "https://bema-website-tau.vercel.app");

export function GET() {
  return new Response(
    `User-agent: *
Allow: /
Disallow: /sermons
Disallow: /events
Disallow: /giving
Sitemap: ${site}/sitemap-index.xml
`,
    {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
      },
    },
  );
}
