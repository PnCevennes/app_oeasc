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
            const aujourdhui = new Date();
            const dateFin = item.date_fin ? new Date(item.date_fin) : null;

            if ($store.getters.droitMax >= 4) {
              return true; // Les admins peuvent éditer n'importe quelle déclaration, même celles dont ils ne sont pas le déclarant ou pour lesquelles ils n'ont pas les droits nécessaires, tant qu'elles ne sont pas expirées
            }
            if ( item.statut === config_variables['STATUT_DECLARATION']['Archivée']) {
              return false; // Les déclarations archivées ne peuvent pas être éditées
            }
            if ($store.getters.user.id_role == item.id_declarant) {
              return true; // Les déclarants peuvent éditer leurs propres déclarations tant qu'elles ne sont pas expirées, même s'ils n'ont pas les droits nécessaires
            } else {
              return false; // Les autres utilisateurs ne peuvent éditer que les déclarations dont ils sont le déclarant ou pour lesquelles ils ont les droits nécessaires, tant qu'elles ne sont pas expirées
            }

          },
        },
        {
          title: 'Renouveler la déclaration',
          icon: 'mdi-refresh',
          to: ({ item }) => `/declaration/actualisation_declaration?id=${item.id_declaration}&action=oui&keySession=all`,
          condition: ({ item, $store }) => {
            const aujourdhui = new Date();
            const dateFin = item.date_fin ? new Date(item.date_fin) : null;
          
            if ((dateFin > aujourdhui) 
              || item.statut === config_variables['STATUT_DECLARATION']['Archivée']
              || item.b_valid === false) {
              return false; // Les déclarations archivées ne peuvent pas être renouvelées, même par les admins
            }

            if (($store.getters.droitMax >= 4)) {
              return true; // Les admins peuvent renouveler n'importe quelle déclaration
            }else if ( $store.getters.user.id_role == item.id_declarant) {
              return true; // Les déclarants et les utilisateurs ayant les droits nécessaires peuvent renouveler les déclarations expirées dont ils sont le déclarant ou pour lesquelles ils ont les droits nécessaires
            }else {
              return false; // Les autres utilisateurs ne peuvent renouveler que les déclarations expirées dont ils sont le déclarant ou pour lesquelles ils ont les droits nécessaires
            }
          
          },
          
        },

        {
          title: 'Envoyer un mail de relance',
          icon: 'mdi-email-send',
          to: ({ item }) => {
            return `/declaration/voir_declaration/${item.id_declaration}?relance=true&keySession=all`;
          },
          condition: ({ item, $store }) => {
            const aujourdhui = new Date();
            const dateFin = item.date_fin ? new Date(item.date_fin) : null;

            if ((dateFin > aujourdhui) 
              || item.statut === config_variables['STATUT_DECLARATION']['Archivée']
              || item.b_valid === false
              || $store.getters.droitMax < 4) {
              return false; // Les déclarations archivées ne peuvent pas être renouvelées, même par les admins
            }else {
              return true; // Les admins peuvent envoyer une relance pour n'importe quelle déclaration expirée, même celles dont ils ne sont pas le déclarant ou pour lesquelles ils n'ont pas les droits nécessaires
            }

            
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
            // this.$store.commit('declarations', {});
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
