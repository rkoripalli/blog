// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import remarkBasePath from './src/lib/remark-base-path.mjs';
import rehypeFigures from './src/lib/rehype-figures.mjs';

// GitHub Pages project site: everything lives under /blog/.
// Post URLs match the old Hugo site (/blog/posts/<slug>/) so existing links keep working.
const base = '/blog';

export default defineConfig({
  site: 'https://rkoripalli.github.io',
  base,
  trailingSlash: 'always',
  integrations: [mdx(), sitemap()],
  markdown: {
    remarkPlugins: [[remarkBasePath, { base }]],
    rehypePlugins: [rehypeFigures],
    shikiConfig: { theme: 'github-dark-default', wrap: false },
  },
});
