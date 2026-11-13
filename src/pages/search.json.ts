import { getPosts, summary, url } from '../lib/site';

export async function GET() {
  const posts = await getPosts();
  const items = posts.map((p) => ({
    title: p.data.title,
    url: url(`posts/${p.id}/`),
    date: p.data.date.toISOString().slice(0, 10),
    sheet: p.sheet,
    summary: summary(p, 200),
    tags: p.data.tags,
    text: (p.body ?? '').replace(/```[\s\S]*?```/g, ' ').replace(/[#*_`>\[\]()!-]/g, ' ').replace(/\s+/g, ' ').toLowerCase(),
  }));
  return new Response(JSON.stringify(items), { headers: { 'Content-Type': 'application/json' } });
}
