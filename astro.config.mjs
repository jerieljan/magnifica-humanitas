import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://reader-magnifica-humanitas.vercel.app',
  output: 'static',
  compressHTML: true,
  trailingSlash: 'always',
  integrations: [sitemap()],
});
