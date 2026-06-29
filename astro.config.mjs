import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://grupo-codec.netlify.app',
  integrations: [tailwind()],
});
