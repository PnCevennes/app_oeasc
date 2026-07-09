// Vuetify 2 détectait automatiquement, par icône, si la chaîne passée à <v-icon> était une classe
// CSS toute faite (mdi-xxx, fa-xxx, contient un tiret) ou un nom de ligature Material Icons
// (report_problem, show_chart, ...), et choisissait le rendu en conséquence. Vuetify 3 a supprimé
// cette détection (une seule iconset par défaut pour toute l'app) ; ce composant la reproduit pour
// ne pas avoir à réécrire les ~15 icônes mdi-*/fa-* codées en dur dans templates et fichiers de
// config (menu.js, etc.) à travers tout le projet.
import { h } from 'vue';

const app = {
  // équivalents minimaux de VClassIcon/VLigatureIcon (internes à vuetify, non exposés par son
  // package.json "exports", donc réimplémentés ici plutôt qu'importés en profondeur)
  component: (props) => {
    const icon = typeof props.icon === 'string' ? props.icon : '';
    const tag = props.tag || 'i';
    // les webfonts mdi/Font Awesome ont besoin d'une classe de base (mdi / fas) en plus de la
    // classe spécifique à l'icône (mdi-eye, fa-tree) pour afficher le glyphe — sans elle le
    // caractère ne s'affiche pas du tout (bouton vide, bug repéré le 2026-07-10 sur les actions
    // voir/éditer d'une table)
    if (icon.startsWith('mdi-')) {
      return h(tag, { class: ['mdi', icon] });
    }
    if (icon.startsWith('fa-')) {
      return h(tag, { class: ['fas', icon] });
    }
    if (icon.includes('-')) {
      return h(tag, { class: icon });
    }
    return h(tag, { class: 'material-icons' }, [icon]);
  },
};

export { app };
