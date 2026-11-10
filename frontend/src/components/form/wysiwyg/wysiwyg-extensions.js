// Extensions et conversions de l'éditeur visuel (Tiptap) des contenus (pages, actualités).
//
// Les contenus existants mêlent du markdown, du HTML et des COMPOSANTS VUE
// (<restitution>, <content-img>, <v-icon>, <a :href="…">…) interprétés à l'affichage par
// v-runtime-template (voir content.vue). Tiptap supprime tout ce qu'il ne connaît pas : avant de
// charger un contenu dans l'éditeur, chaque élément « inconnu » est donc remplacé par un
// marqueur opaque qui conserve son code source tel quel (dans un attribut, que le DOM ne
// modifie pas : la casse des noms de composants et d'attributs est ainsi préservée). À
// l'enregistrement, les marqueurs sont remis en place.
import { Node, mergeAttributes } from '@tiptap/core';
import Image from '@tiptap/extension-image';
import { DOMSerializer } from '@tiptap/pm/model';
import { marked } from 'marked';

import { MARQUE_HTML, estContenuHtml } from './wysiwyg-marque.js';

// éléments que l'éditeur sait lire et écrire
const CONNUS = new Set([
  'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'strike', 'del',
  'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'hr',
  'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'colgroup', 'col', 'a', 'img', 'div', 'span',
]);
const VIDES = new Set(['br', 'hr', 'img', 'col', 'input', 'source', 'meta', 'link', 'area', 'base', 'embed', 'track', 'wbr']);
// éléments dont l'attribut style est lu par l'éditeur (alignement, couleur, taille)
const STYLE_LU = new Set(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'td', 'th', 'table', 'colgroup', 'col']);
// éléments qui restent dans le texte (les autres sont des blocs)
const BALISE = /<(\/?)([a-zA-Z][\w:.-]*)((?:"[^"]*"|'[^']*'|[^>"'])*)>/g;
const ATTRIBUT = /([^\s=/"']+)(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?/g;

const nomsAttributs = (attrs) => [...attrs.matchAll(ATTRIBUT)].map((m) => m[1].toLowerCase());

// l'élément doit-il être conservé tel quel (composant Vue, classe, style non géré…) ?
function estOpaque (balise, attrs) {
  const nom = balise.toLowerCase();
  if (!CONNUS.has(nom)) return true;
  // la classe ajoutée par l'éditeur aux images qu'il insère est lue par lui : pas un élément à conserver
  const noms = nomsAttributs(nom === 'img' ? attrs.replace(/\bclass\s*=\s*(["'])img-wysiwyg\1/i, '') : attrs);
  if (noms.some((n) => /^(:|@|#|v-)/.test(n) || n === 'class' || n === 'id' || n === 'name')) return true;
  if (nom === 'div' && noms.length) return true;
  if (noms.includes('style') && !STYLE_LU.has(nom)) return true;
  return false;
}

const echappeAttribut = (texte) => texte
  .replace(/&/g, '&amp;')
  .replace(/"/g, '&quot;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;');

function etiquette (brut, balise) {
  const texte = brut.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
  return texte ? `${balise} · ${texte.length > 28 ? texte.slice(0, 28) + '…' : texte}` : balise;
}

// position de fin de l'élément ouvert en `debut` (balise fermante du même nom, imbrications
// comptées) ; null si jamais refermé
function trouveFin (source, nom, debut) {
  const re = new RegExp(`<(/?)${nom.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?=[\\s/>])((?:"[^"]*"|'[^']*'|[^>"'])*)>`, 'gi');
  re.lastIndex = debut;
  let niveau = 1;
  let fin = null;
  let f;
  while (niveau > 0 && (f = re.exec(source))) {
    if (f[1]) niveau--;
    else if (!/\/\s*$/.test(f[2])) niveau++;
    fin = re.lastIndex;
  }
  return niveau > 0 ? null : fin;
}

// html -> html où chaque élément à conserver est remplacé par un marqueur
export function protegeComposants (html) {
  const source = html.replace(/<!--[\s\S]*?-->/g, '');
  let sortie = '';
  let curseur = 0;
  let profondeur = 0; // éléments connus ouverts : 0 = au niveau racine du contenu
  BALISE.lastIndex = 0;
  let m;
  while ((m = BALISE.exec(source))) {
    const [balise, fermante, nom, attrs] = m;
    const bas = nom.toLowerCase();
    if (fermante) {
      if (profondeur > 0) profondeur--;
      continue;
    }
    // image de l'éditeur (div.img-content[data-img-wysiwyg] : figure, légende…) : lue telle quelle
    // par l'éditeur, son contenu n'est pas à protéger
    if (bas === 'div' && /(^|\s)data-img-wysiwyg(\s|=|$)/.test(attrs)) {
      const finImage = trouveFin(source, nom, m.index + balise.length);
      if (finImage) BALISE.lastIndex = finImage;
      continue;
    }
    const autoFermee = /\/\s*$/.test(attrs) || VIDES.has(bas);
    if (!estOpaque(nom, attrs)) {
      if (!autoFermee) profondeur++;
      continue;
    }
    // fin de l'élément : sa balise fermante (jamais refermé : la seule balise ouvrante)
    let fin = m.index + balise.length;
    if (!autoFermee) fin = trouveFin(source, nom, fin) ?? fin;
    const brut = source.slice(m.index, fin);
    const bloc = profondeur === 0;
    const marqueur = bloc ? 'div' : 'span';
    sortie += source.slice(curseur, m.index) +
      `<${marqueur} data-composant="${echappeAttribut(brut)}" data-label="${echappeAttribut(etiquette(brut, nom))}"></${marqueur}>`;
    curseur = fin;
    BALISE.lastIndex = fin;
  }
  return sortie + source.slice(curseur);
}

// contenu enregistré (markdown ancien ou HTML de l'éditeur) -> HTML pour l'éditeur
export function contenuVersEditeur (contenu) {
  if (!contenu) return '';
  const html = estContenuHtml(contenu) ? contenu.slice(MARQUE_HTML.length) : marked(contenu);
  return protegeComposants(html);
}

// HTML de l'éditeur -> contenu à enregistrer (marqueurs remplacés par le code d'origine)
export function editeurVersContenu (editor) {
  if (editor.isEmpty) return '';
  const conteneur = document.createElement('div');
  conteneur.innerHTML = editor.getHTML().replace(/(<p><\/p>)+$/, '');
  const bruts = [];
  conteneur.querySelectorAll('[data-composant]').forEach((el) => {
    bruts.push(el.getAttribute('data-composant'));
    el.replaceWith(document.createTextNode(`${bruts.length - 1}`));
  });
  const html = conteneur.innerHTML.replace(/(\d+)/g, (_, i) => bruts[Number(i)]);
  return MARQUE_HTML + html;
}

// --- aperçu des <content-img> (ancienne méthode d'insertion d'images) ---
// propriétés d'un <content-img …> (src, center, float, width, height, title, source,
// risetitle) ; null si le code n'en est pas un ou n'a pas de src fixe
export function proprietesContentImg (brut) {
  const balise = (brut || '').trim().match(/^<content-img((?:"[^"]*"|'[^']*'|[^>"'])*)>/i);
  if (!balise) return null;
  const props = {};
  for (const m of balise[1].matchAll(/([^\s=/"'>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g)) {
    props[m[1].toLowerCase()] = m[2] ?? m[3] ?? m[4] ?? '';
  }
  return props.src ? props : null;
}

// structure DOM identique à celle de content-img.vue (mêmes classes : content.css s'applique)
function apercuContentImg (balise, attrsNoeud, props, chemin) {
  const flottant = ['left', 'right'].find((c) => props.float === c || (props.float === '' && props[c] !== undefined)) ||
    ['left', 'right'].find((c) => props[c] !== undefined);
  const classes = ['composant-cms', 'composant-img', 'img-content'];
  if (props.center !== undefined) classes.push('center');
  if (flottant) classes.push('float', flottant);
  if (props.risetitle !== undefined) classes.push('risetitle');
  const titre = `${props.title || props.src} ${props.source || ''}`.trim();
  const attrsImg = { src: `${chemin}${props.src}`, title: titre, alt: titre };
  if (props.width) attrsImg.width = props.width;
  if (props.height) attrsImg.height = props.height;
  const legende = props.title || props.source
    ? [['figcaption', ['div', { class: 'img-text' }, props.title || '', ...(props.source ? [['i', { class: 'source' }, ` - ${props.source}`]] : [])]]]
    : [];
  return [
    balise,
    mergeAttributes(attrsNoeud, {
      class: classes.join(' '),
      contenteditable: 'false',
      ...(props.width ? { style: `width:${props.width}` } : {}),
    }),
    ['figure', ['img', attrsImg], ...legende],
  ];
}

// --- noeuds opaques : un composant Vue (ou tout élément conservé tel quel) ---
function noeudComposant (name, balise, inline) {
  return Node.create({
    name,
    group: inline ? 'inline' : 'block',
    inline,
    atom: true,
    selectable: true,
    draggable: true,
    addOptions () {
      // adresse des images du serveur (mediaImgPath), pour l'aperçu des <content-img>
      return { cheminImages: '' };
    },
    addAttributes () {
      return {
        brut: {
          default: '',
          parseHTML: (el) => el.getAttribute('data-composant'),
          renderHTML: (attrs) => ({ 'data-composant': attrs.brut }),
        },
        etiquette: {
          default: '',
          parseHTML: (el) => el.getAttribute('data-label'),
          renderHTML: (attrs) => ({ 'data-label': attrs.etiquette }),
        },
      };
    },
    parseHTML () {
      return [{ tag: `${balise}[data-composant]` }];
    },
    renderHTML ({ node, HTMLAttributes }) {
      const props = proprietesContentImg(node.attrs.brut);
      // toujours un <div>, même pour un noeud en ligne (<p><content-img/></p> en markdown) :
      // content-img.vue produit un div, et les styles .img-content de content.css visent div.img-content
      if (props) return apercuContentImg('div', HTMLAttributes, props, this.options.cheminImages);
      return [balise, mergeAttributes(HTMLAttributes, { class: 'composant-cms', contenteditable: 'false' })];
    },
  });
}

export const ComposantBloc = noeudComposant('composantBloc', 'div', false);
export const ComposantEnLigne = noeudComposant('composantEnLigne', 'span', true);

// un code saisi à la main est-il à placer dans le texte (icône, lien…) plutôt qu'en bloc ?
export const estEnLigne = (brut) => /^<(v-icon|a|cite|q|span|i|b|u|em|strong|small|sub|sup)[\s>]/i.test(brut.trim());

export const attributsComposant = (brut) => {
  const nom = (brut.trim().match(/^<([a-zA-Z][\w:.-]*)/) || [])[1] || 'composant';
  return { brut: brut.trim(), etiquette: etiquette(brut, nom) };
};

// --- image de l'éditeur : légende, auteur, position (gauche / centre / droite / flottante),
// titre sur l'image, lien, largeur en px ---
//
// HTML produit = celui de content-img.vue (div.img-content > figure > img + figcaption) : les
// styles .img-content de content.css s'appliquent donc à l'identique dans l'éditeur et sur le
// site. Les données de l'image sont aussi écrites en data-* sur le div, qui font foi à la relecture.
// Un fichier du serveur (nom simple, sans « / » ni protocole) est écrit avec le chemin des
// images du site : `:src="imgPath + 'nom.jpg'"` (imgPath : computed de content.vue), ce qui évite
// de figer le domaine dans le texte.
export const estFichierMedia = (src) => !!src && !/^([a-z][a-z0-9+.-]*:|\/|\.)/i.test(src);
const exprChemin = (nom) => `imgPath + '${String(nom).replace(/\\/g, '\\\\').replace(/'/g, "\\'")}'`;

export const POSITIONS_IMAGE = {
  center: 'center',
  right: 'align-right',
  'float-left': 'float left',
  'float-right': 'float right',
};

// adresse affichable d'une image dans l'éditeur
export const adresseImage = (src, chemin = '') => (estFichierMedia(src) ? `${chemin}${src}` : src);

// description DOM (format renderHTML de ProseMirror) d'une image ; `liaison` : écrit les
// adresses de fichiers du serveur sous forme d'expression Vue (enregistrement) plutôt que
// d'adresse complète (affichage dans l'éditeur)
function structureImage (a, { chemin = '', liaison = false } = {}) {
  const adresse = (attr, valeur) => (estFichierMedia(valeur) && liaison
    ? { [`:${attr}`]: exprChemin(valeur) }
    : { [attr]: adresseImage(valeur, chemin) });
  const classes = ['img-content', 'img-wysiwyg'];
  if (POSITIONS_IMAGE[a.alignement]) classes.push(...POSITIONS_IMAGE[a.alignement].split(' '));
  if (a.titreSurImage) classes.push('risetitle');
  const titre = `${a.titre || a.alt || a.src || ''} ${a.source || ''}`.trim();
  const img = ['img', { ...adresse('src', a.src), title: titre, alt: a.alt || titre }];
  const contenu = a.lien
    ? ['a', { ...adresse('href', a.lien), target: '_blank', rel: 'noopener noreferrer' }, img]
    : img;
  const legende = a.titre || a.source
    ? [['figcaption', ['div', { class: 'img-text' }, a.titre || '', ...(a.source ? [['i', { class: 'source' }, ` - ${a.source}`]] : [])]]]
    : [];
  return [
    'div',
    {
      class: classes.join(' '),
      ...(a.largeur ? { style: `width:${a.largeur}px` } : {}),
      'data-img-wysiwyg': a.src || '',
      ...(a.alt ? { 'data-alt': a.alt } : {}),
      ...(a.titre ? { 'data-titre': a.titre } : {}),
      ...(a.source ? { 'data-source': a.source } : {}),
      ...(a.lien ? { 'data-lien': a.lien } : {}),
      ...(a.alignement ? { 'data-align': a.alignement } : {}),
      ...(a.largeur ? { 'data-largeur': String(a.largeur) } : {}),
      ...(a.titreSurImage ? { 'data-risetitre': '' } : {}),
    },
    ['figure', contenu, ...legende],
  ];
}

const nombre = (v) => {
  const n = parseInt(v, 10);
  return Number.isFinite(n) && n > 0 && /^\s*\d+(\.\d+)?(px)?\s*$/.test(String(v)) ? n : null;
};

const attributImage = (defaut = null) => ({ default: defaut, rendered: false, parseHTML: () => null });

const LARGEUR_MIN = 40;

export const ImageLegende = Image.extend({
  addOptions () {
    return { ...this.parent?.(), cheminImages: '' };
  },
  addAttributes () {
    return {
      src: attributImage(),
      alt: attributImage(),
      titre: attributImage(), // légende
      source: attributImage(), // auteur
      lien: attributImage(), // image agrandie au clic
      alignement: attributImage(), // null (gauche) | center | right | float-left | float-right
      largeur: attributImage(), // px
      titreSurImage: attributImage(false),
    };
  },
  parseHTML () {
    return [
      {
        tag: 'div[data-img-wysiwyg]',
        priority: 60,
        getAttrs: (el) => ({
          src: el.getAttribute('data-img-wysiwyg'),
          alt: el.getAttribute('data-alt'),
          titre: el.getAttribute('data-titre'),
          source: el.getAttribute('data-source'),
          lien: el.getAttribute('data-lien'),
          alignement: el.getAttribute('data-align'),
          largeur: nombre(el.getAttribute('data-largeur')),
          titreSurImage: el.hasAttribute('data-risetitre'),
        }),
      },
      // image seule : markdown ![](…) ou première version de l'éditeur (<img data-align width>)
      {
        tag: 'img[src]:not([src^="data:"])',
        getAttrs: (el) => ({
          src: el.getAttribute('src'),
          alt: el.getAttribute('alt'),
          alignement: el.getAttribute('data-align'),
          largeur: nombre(el.getAttribute('width')),
        }),
      },
    ];
  },
  renderHTML ({ node }) {
    return structureImage(node.attrs, { liaison: true });
  },
  addNodeView () {
    const chemin = this.options.cheminImages;
    return ({ node, getPos, editor }) => {
      let noeud = node;
      let selectionne = false;
      const rendu = () => DOMSerializer.renderSpec(document, structureImage(noeud.attrs, { chemin })).dom;
      const dom = rendu();
      dom.draggable = true;

      // les poignées d'angle changent la largeur (px) ; la hauteur suit les proportions
      const ajoutePoignees = () => {
        if (!editor.isEditable) return;
        ['hg', 'hd', 'bg', 'bd'].forEach((coin) => {
          const poignee = document.createElement('span');
          poignee.className = 'poignee-img';
          poignee.dataset.coin = coin;
          poignee.addEventListener('pointerdown', (event) => {
            event.preventDefault();
            event.stopPropagation();
            poignee.setPointerCapture(event.pointerId);
            const depart = dom.getBoundingClientRect().width;
            const x0 = event.clientX;
            const signe = coin.endsWith('g') ? -1 : 1;
            let largeur = Math.round(depart);
            const surMouvement = (e) => {
              largeur = Math.max(LARGEUR_MIN, Math.round(depart + signe * (e.clientX - x0)));
              dom.style.width = `${largeur}px`;
            };
            const surRelache = () => {
              poignee.removeEventListener('pointermove', surMouvement);
              poignee.removeEventListener('pointerup', surRelache);
              poignee.removeEventListener('pointercancel', surRelache);
              const position = getPos();
              if (position == null) return;
              editor.view.dispatch(
                editor.state.tr.setNodeMarkup(position, undefined, { ...noeud.attrs, largeur })
              );
            };
            poignee.addEventListener('pointermove', surMouvement);
            poignee.addEventListener('pointerup', surRelache);
            poignee.addEventListener('pointercancel', surRelache);
          });
          dom.append(poignee);
        });
      };
      ajoutePoignees();

      // un lien dans l'éditeur ne doit pas emmener ailleurs
      dom.addEventListener('click', (event) => {
        if (event.target instanceof Element && event.target.closest('a')) event.preventDefault();
      });

      return {
        dom,
        update: (mis) => {
          if (mis.type !== noeud.type) return false;
          noeud = mis;
          // le div racine est conservé (ProseMirror le référence) : attributs et contenu recopiés
          const neuf = rendu();
          [...dom.attributes].forEach((att) => dom.removeAttribute(att.name));
          [...neuf.attributes].forEach((att) => dom.setAttribute(att.name, att.value));
          dom.draggable = true;
          if (selectionne) dom.classList.add('ProseMirror-selectednode');
          dom.replaceChildren(...neuf.childNodes);
          ajoutePoignees();
          return true;
        },
        selectNode: () => {
          selectionne = true;
          dom.classList.add('ProseMirror-selectednode');
        },
        deselectNode: () => {
          selectionne = false;
          dom.classList.remove('ProseMirror-selectednode');
        },
        stopEvent: (event) => event.target instanceof Element && !!event.target.closest('.poignee-img'),
        ignoreMutation: () => true,
      };
    };
  },
});
