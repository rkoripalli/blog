// RSS feed. Kept at /blog/index.xml (the Hugo path) because Buttondown's
// RSS-to-email automation watches this exact URL.
import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { getPosts, SITE, summary, url } from '../lib/site';

export async function GET(context: APIContext) {
  const posts = await getPosts();
  return rss({
    title: SITE.title,
    description: SITE.description,
    site: new URL(url(''), context.site),
    items: posts.map((p) => ({
      title: p.data.title,
      pubDate: p.data.date,
      description: summary(p, 400),
      link: url(`posts/${p.id}/`),
      categories: p.data.tags,
    })),
    customData: '<language>en-us</language>',
  });
}
