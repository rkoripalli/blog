// Turn a paragraph that holds only an image into a numbered figure:
// <figure class="fig"><img ...><figcaption><span>FIG 3</span> alt text</figcaption></figure>
export default function rehypeFigures() {
  return (tree) => {
    let n = 0;
    const visit = (node) => {
      if (!node.children) return;
      node.children = node.children.map((child) => {
        if (child.type === 'element' && child.tagName === 'p') {
          const kids = child.children.filter((c) => !(c.type === 'text' && !c.value.trim()));
          if (kids.length === 1 && kids[0].type === 'element' && kids[0].tagName === 'img') {
            n += 1;
            const img = kids[0];
            img.properties = { ...img.properties, loading: 'lazy', decoding: 'async' };
            const alt = String(img.properties.alt || '');
            return {
              type: 'element',
              tagName: 'figure',
              properties: { className: ['fig'] },
              children: [
                img,
                {
                  type: 'element',
                  tagName: 'figcaption',
                  properties: {},
                  children: [
                    { type: 'element', tagName: 'span', properties: { className: ['fig-no'] }, children: [{ type: 'text', value: `FIG ${n}` }] },
                    { type: 'text', value: alt ? ' ' + alt : '' },
                  ],
                },
              ],
            };
          }
        }
        visit(child);
        return child;
      });
    };
    visit(tree);
  };
}
