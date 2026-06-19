// import { copy } from "@/core/js/util/util";

export default {
  group: 'in',
  name: 'realisation',
  label: 'Réalisation',
  serverSide: true,

  options: {
    // Ajoute des param à la requête get pour filtrer les données
    page: 1, // on affiche la première page par défaut
    sortBy: ['id_realisation'], // tri par défaut
    sortDesc: [true], // tri en ordre décroissant
    // fields: [ //les des champs des modèles à intégrer à la requête get
    //   "secteur.id_secteur", "secteur.nom_secteur",
    // ]
  },

  columns: [
    'id_realisation',
    'date_realisation',
    'circuit',
    'secteur',
    'serie',
    'valide_ZC',
    'valide_PNC',
    'observers_table',
    'cerfs',
    'chevreuils',
    'lievres',
    'renards',
  ],
  defs: {
    observers_table: {
      label: 'Observateurs',
    },

    id_realisation: {
      label: 'ID',
      hidden: true,
    },
    date_realisation: {
      type: 'date',
      label: 'Date',
      required: true,
    },
    circuit: {
      label: 'Circuit',
      storeName: 'inCircuit',
      type: 'list_form',
      list_type: 'autocomplete',
      returnObject: true,
      dataReloadOnSearch: true,
      required: true,
      params: { actif: true },
    },
    secteur: {
      text: 'Secteur',
      label: 'Secteur',
      // storeName: 'commonsSecteur',
      displayFieldName: 'code_secteur',
      type: 'list_form',
      list_type: 'select',
      returnObject: true,
      dataReloadOnSearch: true,
      // preProcess: (d) => d.circuit.secteur,
      display: (d) => (
        d.circuit && d.circuit.secteur && d.circuit.secteur.code_secteur ? d.circuit.secteur.code_secteur : ''
      ),
    },

    observers: {
      type: 'list_form',
      list_type: 'combobox',
      label: 'Observateurs',
      maxLength: 4,
      multiple: true,
      storeName: 'inObserver',
      returnObject: true,
      // dataReloadOnSearch: true,
      display: (d) => (d && d.length ? d.map((dd) => dd.nom_observer).join(', ') : ''),
    },

    // on n'affiche valide_ZC que si le secteur du circuit est "Causse-Gorges"
    valide_ZC: {
      label: 'Valide ZC',
      type: 'bool_switch',
      display: (d) => (
        d.circuit && d.circuit.secteur && d.circuit.secteur.code_secteur === 'CAUS' ? d.valide_ZC : ''
      ),
    },
    valide_PNC: {
      label: 'Valide PNC',
      type: 'bool_switch',
    },

    temperature: {
      label: 'Température',
      type: 'list_form',
      list_type: 'select',
      items: ['Froid', 'Frais', 'Doux', 'Chaud'],
    },
    temps: {
      label: 'Temps',
      type: 'list_form',
      list_type: 'select',
      items: ['Sec', 'Puie fine', 'Brouillard', 'Neige'],
    },
    vent: {
      label: 'Vent',
      type: 'list_form',
      list_type: 'select',
      items: ['Nul', 'Faible', 'Moyen', 'Fort'],
    },
    observations: {
      type: 'list',
      label: 'Comptage',
      forms: ['id_espece', 'nb', 'id_observation'],
      required: true,
    },
    id_espece: {
      type: 'list_form',
      list_type: 'select',
      label: 'Espece',
      storeName: 'commonsEspece',
      required: true,
    },
    nb: {
      type: 'number',
      label: "Nombre d'individus",
      min: 0,
      required: true,
    },
    groupes: {
      type: 'number',
      label: 'Nombre de groupes de cerfs',
      min: '0',
    },
    serie: {
      type: 'number',
      label: 'Série',
      min: '0',
      required: true,
    },
    id_observation: {
      label: 'ID observation',
      type: 'text',
      hidden: true,
    },
    cerfs: {
      text: 'Cerfs',
      type: 'number',
    },
    chevreuils: {
      text: 'Chevreuils',
      type: 'number',
    },
    lievres: {
      text: 'Lièvres',
      type: 'number',
    },
    renards: {
      text: 'Renards',
      type: 'number',
    },
  },
  form: {
    groups: [
      {
        title: 'Informations',
        forms: ['date_realisation', 'circuit', 'serie', 'observers'],
      },
      {
        title: 'Validation',
        condition: ({ baseModel }) => {
          return baseModel.circuit && baseModel.circuit.secteur && baseModel.circuit.secteur.code_secteur === 'CAUS';
        },
        forms: ['valide_ZC', 'valide_PNC'],
      },
      {
        title: 'Validation',
        condition: ({ baseModel }) => {
          return baseModel.circuit && baseModel.circuit.secteur && baseModel.circuit.secteur.code_secteur != 'CAUS';
        },
        forms: ['valide_PNC'],
      },
      {
        title: 'Météo',
        direction: 'row',
        forms: ['temperature', 'temps', 'vent'],
      },
      {
        title: 'Observations',
        forms: ['groupes', 'observations'],
      },
    ],
    value: {
      observations: [
        { id_espece: 1, nb: 0 },
        { id_espece: 2, nb: 0 },
        { id_espece: 3, nb: 0 },
        { id_espece: 4, nb: 0 },
      ],
      //on n'affiche valide_ZC que si le secteur du circuit est "Causse-Gorges", on le met à true par défaut pour éviter les erreurs de validation
      
    },
    // action: {
    // preProcess: ({ baseModel }) => {
    //   const out = copy(baseModel);
    //   out.tags = baseModel.tags.map(t => ({
    //     id_observation: t.id_observation,
    //     id_tag: t.id_tag,
    //     valild: t.valid
    //   }));
    //   return out;
    // }
    // }
  },
};
