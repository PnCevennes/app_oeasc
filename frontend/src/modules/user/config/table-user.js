import { config as globalConfig } from '@/config/config';
import formDefsUser from './form-defs-user';

// Édition par un modérateur : utilisateurs de droit strictement inférieur ; sans limite pour le niveau 6
import { peutGererUtilisateur } from '@/config/droits.js';
const editAdmin = (fields) => ({
  condition: ({ $store, baseModel }) =>
    peutGererUtilisateur($store.getters.droitMax, baseModel.id_droit_max),
  action: {
    preProcess: ({ baseModel }) => {
      const data = {};
      fields.forEach((f) => (data[f] = baseModel[f]));
      return data;
    },
    request: {
      url: ({ id }) => `api/user/admin_update/${id}`,
      method: 'POST',
    },
  },
  formDefs: Object.fromEntries(fields.map((f) => [f, formDefsUser[f]])),
});

export default {
  idFieldName: 'id_role',
  labelFieldName: 'nom_complet',
  title: 'Liste des utilisateurs',
  sortBy: ['create_date'],
  sortDesc: [true],
  dense: true,
  striped: true,
  headerDefs: {
    org_mnemo: {
      text: 'Organisme',
      edit: editAdmin(['id_organisme', 'autre_organisme']),
    },
    nom_complet: {
      text: 'Nom, prénom',
    },
    email: {
      text: 'E-mail',
      edit: editAdmin(['email']),
    },
    desc_role: {
      text: 'Rôle',
      edit: editAdmin(['desc_role']),
      display: (d) => {
        const val = d['desc_role'];
        return val.split(' ')[0].split(',')[0];
      },
    },
    id_droit_max: {
      text: 'Droits',
      display: (d) => d.droit_label || d.id_droit_max,
      edit: {
        condition: ({ $store, baseModel }) => {
          return peutGererUtilisateur($store.getters.droitMax, baseModel.id_droit_max);
        },
        action: {
          preProcess: ({ baseModel }) => {
            return {
              id_role: baseModel.id_role,
              id_droit: baseModel.id_droit_max,
              id_application: globalConfig.ID_APPLICATION,
            };
          },
          request: {
            url: 'register/post_usershub/change_application_right',
            method: 'POST',
          },
          onSuccess: ({ data }) => {
            data.id_droit_max = data.id_droit;
            data.droit_label = String(data.id_droit);
          },
        },
        formDefs: {
          id_droit_max: {
            type: 'list_form',
            list_type: 'select',
            url: 'api/user/libelles_droits',
            required: true,
          },
        },
      },
    },
    nb_declarations: {
      text: 'Nb déclarations',
    },
    create_date: {
      text: 'Date inscription',
      type: 'date',
    },
    accept_email: {
      text: 'Accepte Email',
    },
  },
};
