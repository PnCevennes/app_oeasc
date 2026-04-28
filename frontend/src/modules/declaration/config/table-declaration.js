import { apiRequest } from '../../../core/js/data/api.js';
import { displayParcelles, displayDate, displayStatut } from '../declaration.js';
import config_variables from '@/../../config/variables/declaration.json';

export default {
  idFieldName: 'id_declaration',
  dense: true,
  striped: true,
  small: true,
  headerDefs: {
    actions: {
      noSearch: true,
      width: '150px',
      text: 'Actions',
      list: [
        {
          title: 'Voir la déclaration',
          icon: 'mdi-eye',
          to: ({ item }) => `/declaration/voir_declaration/${item.id_declaration}`,
        },
        {
          title: 'Éditer la déclaration',
          icon: 'mdi-pencil',
          to: ({ item }) => `/declaration/modifier_declaration?id=${item.id_declaration}&keySession=all`,
          condition: ({ item, $store }) => {
            // console.log('Condition édition déclaration', {
            //   item,
            //   droitMax: $store.getters.droitMax,
            //   userIdRole: $store.getters.user.id_role,
            //   idDroitMax: item.id_droit_max,
            // });
            return (
              ($store.getters.droitMax > 2) ||
              ($store.getters.droitMax > item.id_droit_max) ||
              (
                $store.getters.user.id_role == item.id_declarant
                && item.date_fin 
                && new Date(item.date_fin) >= new Date()
              )
            );
          },
        },
        {
          title: 'Renouveler la déclaration',
          icon: 'mdi-refresh',
          to: ({ item }) => `/declaration/actualisation_declaration?id=${item.id_declaration}&action=oui&keySession=all`,
          condition: ({ item, $store }) => {
            return (
              item.date_fin && new Date(item.date_fin) < new Date() && // La déclaration est expirée
              item.b_valid === true && // La déclaration est validée
              item.statut !== config_variables['STATUT_DECLARATION']['Archivée'] && // La déclaration n'est pas déjà archivée
              ($store.getters.droitMax > item.id_droit_max || $store.getters.user.id_role == item.id_declarant) // L'utilisateur a les droits pour éditer la déclaration
            );
          },
          
        },

        {
          title: 'Envoyer un mail de relance',
          icon: 'mdi-email-send',
          to: ({ item }) => {
            return `/declaration/voir_declaration/${item.id_declaration}?relance=true&keySession=all`;
          },
          condition: ({ item, $store }) => {
            return (
              item.date_fin && new Date(item.date_fin) < new Date() && // La déclaration est expirée
              item.b_valid === true && // La déclaration est validée
              item.statut !== config_variables['STATUT_DECLARATION']['Archivée'] && // La déclaration n'est pas déjà archivée
              ($store.getters.droitMax > item.id_droit_max || $store.getters.user.id_role == item.id_declarant) // L'utilisateur a les droits pour éditer la déclaration
            );
          },
          // si on clic sur ce bouton, on affiche une boîte de dialogue de confirmation, et si l'utilisateur confirme, on envoie une requête POST à l'API pour envoyer le mail de relance
  
        },

      ],
      sortable: false,
    },
    id_declaration: {
      text: 'Id',
    },
    declarant: {
      text: 'Déclarant',
    },
    org_mnemo: {
      text: 'Organisme',
    },
    // organisme: {
    //   text: "Organisme"
    // },
    secteur: {
      text: 'Secteur',
    },
    declaration_date: {
      text: 'Date déclaration',
      display: (val) => {
        return displayDate(val.declaration_date);
      },
    },
    date_fin: {
      text: 'Date fin validité',
      display: (val) => displayDate(val.date_fin),
    },
    label_foret: {
      text: 'Nom forêt',
    },
    // peuplement_ess_1_mnemo: {
    //   text: 'Ess. objectif',
    // },
    parcelles: {
      text: 'Parcelle(s)',
      display: (val) => displayParcelles(val.parcelles),
    },
    // peuplement_type_mnemo: {
    //   text: 'Type peupl.',
    // },
    // peuplement_origine2_mnemo: {
    //   text: 'Origine plants touchés',
    // },
    degat_type_mnemos: {
      // si besoin d'un peu de place on peut éventuellement retirer cette colonne
      text: 'Type dégâts',
    },
    b_valid: {
      display: (val) => (val.b_valid === true ? 'Oui' : val.b_valid === false ? 'Non' : '?'),
      width: '100px',
      text: 'Validé',
      condition: ({ $store }) => $store.getters.droitMax >= 5,
      edit: {
        preloadData: ({ config, $store, id }) => {
          return apiRequest('get', `api/declaration/declaration?id=${id}`).then((response) => {
            config.value = response.data;
            return response.data;
          });
        },
        action: {
          request: {
            url: 'api/declaration/validate_declaration',
            method: 'POST',
          },
          onsuccess: ({ data }) => {
            // Met à jour la déclaration dans le tableau pour que le changement soit visible en temps réel
            const index = config.value.tableData.value.findIndex(
              (d) => d.id_declaration === data.id_declaration
            );
            // Si la déclaration est trouvée, on met à jour son statut de validation
            if (index !== -1) {
              config.value.tableData.value[index] = {
                ...config.value.tableData.value[index],
                b_valid: data.b_valid,
                // change le statut de la déclaration en "En cours" si elle est validée, ou "Brouillon" si elle est invalidée
              };
            }
          },
        },
        formDefs: {
          b_valid: {
            label: 'Valider cette déclaration (admin seulement)',
            type: 'bool_radio',
            labels: ['Oui', 'Non'],
          },
        },
      },
    },
    statut: {
      text: 'Statut',
      display: (val) => displayStatut(val.statut),
      
    },
    
  },
};
