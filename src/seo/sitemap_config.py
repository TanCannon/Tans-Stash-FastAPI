'''sitemap_config.py (recommended) change the seo static data from here'''

# Define restricted URLs that should not be included in the sitemap
EXCLUDED_ROUTES = ("/api", "/admin", "/uploader", "/logout", "/sitemap.xml", "/robots.txt", "/ads.txt", "/favicon.ico", "/search")

STATIC_PAGES_LASTMOD = {
    "/": "2026-01-14",
    "/about": "2026-01-14",
    "/contact": "2026-01-14",

    "/privacy": "2025-10-01",
    "/terms": "2025-10-01",
    "/disclaimer": "2025-10-01",
    "/faq": "2025-10-01",

    "/tools": "2026-01-14",
    "/tools/ascii-tree-to-zip": "2026-01-14",
    "/tools/character-counter": "2026-01-14",

    "/blog": "2026-01-14",
}
