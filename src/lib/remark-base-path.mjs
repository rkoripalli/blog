// Prefix root-absolute image and link paths ("/images/...") with the site base ("/blog"),
// so posts can keep writing /images/<slug>/x.png like they did on Hugo.
export default function remarkBasePath({ base = '' } = {}) {
  const fix = (url) =>
    typeof url === 'string' && url.startsWith('/') && !url.startsWith('//') && !url.startsWith(base + '/')
      ? base + url
      : url;
  const walk = (node) => {
    if ((node.type === 'image' || node.type === 'link') && node.url) node.url = fix(node.url);
    if (node.children) node.children.forEach(walk);
  };
  return (tree) => walk(tree);
}
