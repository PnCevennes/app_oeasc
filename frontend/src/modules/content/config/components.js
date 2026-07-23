import { defineAsyncComponent } from 'vue';
import { CONTENT as CHASSE_CONTENT } from '@/modules/chasse/index.js';
import { CONTENT as IN_CONTENT } from '@/modules/in/index.js';
import { CONTENT as DECLARATIONS_CONTENT } from '@/modules/declaration/index.js';

// Chargés à la demande (defineAsyncComponent) plutôt qu'en import statique : ce fichier est lui-même
// importé par content.vue dès qu'une seule page CMS est affichée, donc un import statique ici
// (carte Leaflet, dashboards de restitution Highcharts, etc.) faisait charger la quasi-totalité
// du site à chaque navigation, même quand le contenu de la page n'utilise aucun de ces composants.
const val = defineAsyncComponent(() => import('../val.vue'));
const faqDeclaration = defineAsyncComponent(() => import('../faq-declaration.vue'));
const tableAide = defineAsyncComponent(() => import('../table-aide.vue'));
const listePartenaire = defineAsyncComponent(() => import('../liste-partenaire.vue'));
// import declarationTable from '@/modules/declaration/declaration-table.vue';
const baseMap = defineAsyncComponent(() => import('@/components/map/base-map.vue'));
const contentImg = defineAsyncComponent(() => import('../content-img.vue'));
const restitution = defineAsyncComponent(() => import('@/modules/restitution/restitution.vue'));
const restitution2 = defineAsyncComponent(() => import('@/modules/restitution2/restitution.vue'));
const actualiteBandeau = defineAsyncComponent(() => import('../actualites-bandeau.vue'));
const dynamicForm = defineAsyncComponent(() => import('@/components/form/dynamic-form.vue'));
const dynamicFormGroup = defineAsyncComponent(() => import('@/components/form/dynamic-form-group.vue'));

/**
 * @module components
 * @description
 * Ce module exporte un objet contenant différents composants utilisés dans l'application Vue.js.
 *
 * Propriétés :
 * - val : Composant principal pour la gestion des valeurs.
 * - faqDeclaration : Composant pour l'affichage de la FAQ concernant les déclarations.
 * - tableAide : Petite fenetre avec les noms et les contacts des personnes référentes.
 * - declarationTable : Composant pour la gestion des tables de déclaration.
 * - baseMap : Composant pour l'affichage de la carte de base.
 * - contentImg : Composant pour l'affichage des images de contenu.
 * - listePartenaire : Composant pour la liste des partenaires.
 * - actualiteBandeau : Affiche les 4 dernières actualités sur la page d'accueil.
 * - restitution : Composant pour la restitution des données.
 * - restitution2 : Variante du composant de restitution.
 * - dynamicForm : Composant pour la gestion des formulaires dynamiques.
 * - dynamicFormGroup : Composant pour la gestion des groupes de formulaires dynamiques.
 * - ...CHASSE_CONTENT : Inclusion des composants spécifiques à la chasse.
 * - ...IN_CONTENT : Inclusion des composants spécifiques à l'inventaire.
 * - ...DECLARATIONS_CONTENT : Inclusion des composants spécifiques aux déclarations.
 *
 * Ces composants sont utilisés pour construire dynamiquement les différentes parties de l'interface utilisateur.
 */
export default {
  val,
  faqDeclaration,
  tableAide,
  baseMap,
  contentImg,
  listePartenaire,
  actualiteBandeau,
  restitution,
  restitution2,
  dynamicForm,
  dynamicFormGroup,
  ...CHASSE_CONTENT,
  ...IN_CONTENT,
  ...DECLARATIONS_CONTENT,
};
