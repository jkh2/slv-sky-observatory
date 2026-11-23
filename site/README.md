# Observatory entry portal

The public entry portal is a buildless static site. It has distinct paths for observers and contributors, a community page, and a truthful app-status doorway. The terrain illustration is interpretive artwork, not a live map or sensor feed.

## Preview

Serve this directory with any static file server and open `index.html`. The pages use relative links, so they can also be hosted under a path. No account, reporting form, or backend is active in this portal.

## Publishing

The hosted Site uses `.openai/hosting.json` with `dist` as its static output directory. Copy `index.html`, `style.css`, `main.js`, `assets/`, `observe/`, `build/`, `community/`, and `app/` into `dist/` before packaging. Keep `dist/` generated rather than editing it directly. The Sites source checkout and the GitHub repository are separate remotes; mirror reviewed portal changes to both until an automated sync is established.

## Next integration

Replace the `/app/` status page with a link to the secure reporting app once it is deployed and ready. Give the eventual on-site discussion board its own authenticated backend, moderation tools, and privacy policy; the current community page points to public GitHub Issues for project discussion.
