import faqDeclaration from "../faq-declaration";
import tableAide from "../table-aide";
import listePartenaire from "../liste-partenaire";
import declarationTable from "@/modules/declaration/declaration-table";
import baseMap from "@/modules/map/base-map";
import contentImg from "../content-img";
import restitution from "@/modules/restitution/restitution.vue";
import restitution2 from "@/modules/restitution2/restitution.vue";
import actualiteBandeau from "../actualites-bandeau.vue"
import { CONTENT as CHASSE_CONTENT } from "@/modules/chasse/"
import { CONTENT as IN_CONTENT } from "@/modules/in/"
import dynamicForm from "@/components/form/dynamic-form";

export default {
    faqDeclaration,
    tableAide,
    declarationTable,
    baseMap,
    contentImg,
    listePartenaire,
    actualiteBandeau,
    restitution,
    restitution2,
    dynamicForm,
    ...CHASSE_CONTENT,
    ...IN_CONTENT,
  }