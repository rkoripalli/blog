import { getCollection, type CollectionEntry } from 'astro:content';

export const SITE = {
  title: 'Rohan Koripalli',
  shortTitle: 'R. Koripalli · Build logs',
  tagline: "Notes from a house that's never quite finished.",
  description:
    'Build logs from my house, my 1996 F-150, my homelab and a FIRST Robotics shop. Drawings, wiring, code, and what I would change next time.',
  buttondownUsername: 'rkoripalli',
  github: 'https://github.com/rkoripalli',
  linkedin: 'https://linkedin.com/in/rkoripalli',
};

const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');

/** Join a path onto the site base: url('posts/') -> /blog/posts/ */
export function url(path = '') {
  if (/^https?:\/\//.test(path)) return path;
  return `${BASE}/${path.replace(/^\//, '')}`;
}

/** Same slug rules Hugo used for tags ("home automation" -> "home-automation"). */
export function tagSlug(tag: string) {
  return tag.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

export function tagLabel(tag: string) {
  const special: Record<string, string> = { esphome: 'ESPHome', meta: 'Meta' };
  return special[tag.toLowerCase()] ?? tag.replace(/\b\w/g, (c) => c.toUpperCase());
}

export type Post = CollectionEntry<'posts'> & { sheet: string; minutes: number };

/** Published posts, newest first, each with a sheet number (oldest = 001) and reading time. */
export async function getPosts(): Promise<Post[]> {
  const all = await getCollection('posts', ({ data }) => import.meta.env.DEV || !data.draft);
  const oldestFirst = all.sort((a, b) => a.data.date.valueOf() - b.data.date.valueOf());
  return oldestFirst
    .map((p, i) => {
      const words = (p.body ?? '').split(/\s+/).filter(Boolean).length;
      return Object.assign(p, {
        sheet: String(i + 1).padStart(3, '0'),
        minutes: Math.max(1, Math.round(words / 220)),
      });
    })
    .reverse();
}

export function isoDate(d: Date) {
  return d.toISOString().slice(0, 10);
}

/** First paragraph of the body as a fallback summary when a post has no description. */
export function summary(p: Post, max = 180) {
  if (p.data.description) return p.data.description;
  const text = (p.body ?? '')
    .split(/\n\s*\n/)
    .map((s) => s.trim())
    .find((s) => s && !s.startsWith('#') && !s.startsWith('!') && !s.startsWith('<') && !s.startsWith('import'));
  const plain = (text ?? '').replace(/[*_`]/g, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
  return plain.length > max ? plain.slice(0, plain.lastIndexOf(' ', max)) + '…' : plain;
}

export function coverUrl(p: Post) {
  return p.data.cover ? url(p.data.cover.image) : undefined;
}
