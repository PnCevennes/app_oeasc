// Marque d'un contenu enregistré par l'éditeur visuel : il est du HTML, à ne pas repasser par
// marked à l'affichage (les anciens contenus, sans marque, restent du markdown).
// Fichier séparé et minuscule : content.vue (chargé par tous les visiteurs) l'importe sans
// embarquer Tiptap.
export const MARQUE_HTML = '<!--wysiwyg-->';

export const estContenuHtml = (texte) => typeof texte === 'string' && texte.startsWith(MARQUE_HTML);
