# Observatory entry portal

The public entry portal is a buildless static site. It has distinct paths for observers and contributors, a community page, and a truthful app-status doorway. The terrain illustration is interpretive artwork, not a live map or sensor feed.

## Preview

Serve this directory with any static file server and open `index.html`. The pages use relative links, so they can also be hosted under a path. No account, reporting form, or backend is active in this portal.

## Publishing

The repository's `.github/workflows/pages.yml` publishes this directory to GitHub Pages when portal files land on `main`, or when the workflow is run manually. It prepares a clean artifact with `index.html` at its root. GitHub Pages must be enabled with **GitHub Actions** as its source in repository Settings → Pages; the workflow needs `pages: write` and `id-token: write`. Keep changes in `site/` and review them through pull requests.

The earlier ChatGPT Sites deployment is separate. Its `.openai/hosting.json` and generated `dist/` are for that deployment and are not used by GitHub Pages.

## Next integration

Replace the `/app/` status page with a link to the secure reporting app once it is deployed and ready. Give the eventual on-site discussion board its own authenticated backend, moderation tools, and privacy policy; the current community page points to public GitHub Issues for project discussion.
