<template>
  <div>
    
    <!-- fenetre modal qui apparait lorqu'on veut supprimer une ligne -->
    <v-dialog persistent max-width="600px" v-model="deleteModal">
      <v-card>
        <v-card-title>
          <v-icon large>warning</v-icon>
          Êtes vous sûr de vouloir supprimer la ligne?
        </v-card-title>

        <v-card-text>
          <v-checkbox
            dense
            tiny
            v-model="deleteWithoutWarning"
            label="Ne plus afficher ce message avant la suppression"
          ></v-checkbox>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="green darken-1"
            text
            @click="
              deleteRow(idToDelete);
              idToDelete = null;
              deleteModal = false;
            "
          >
            Oui
          </v-btn>

          <v-btn
            color="green darken-1"
            text
            @click="
              idToDelete = null;
              deleteModal = false;
            "
          >
            Non
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-card>

      <v-card-title>
        {{ option_table.title }}
        <v-spacer></v-spacer>
      </v-card-title>


      <v-data-table
        :options.sync="options"
        :class="option_table.style"
        :items-per-page=option_table.itemsPerPage
        :headers="columns"
        :items="mappedItems"
        multi-sort
        :dense=option_table.dense
        :loading="!responseData"
        :server-items-length="configTable.serverSide && itemsServerCount"
        loading-text="Chargement en cours... merci de patienter"
      >

        <template v-slot:header>
            <tr>
              <td>
                <v-tooltip top>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      v-on="on"
                      color="primary"
                      small

                      icon
                      @click="edit('actions')"
                      ><v-icon>fa-plus</v-icon></v-btn
                    >
                  </template>
                  
                  <span>Ajouter une nouvelle ligne au tableau</span>
                </v-tooltip>
              </td>

                <td v-for="column of columns" :key="column.key" :style="{ paddingLeft: '5px', paddingRight: '5px' }">

                <v-text-field
                  dense
                  v-model="searchs[column.value]"
                  type="text"
                  :label="column.title"

                ></v-text-field>


                
                </td>
            </tr>
          </template>

          <template v-slot:body.prepend>
            <tr v-for="(item, index) in mappedItems" :key="index">
              <td>

                <v-btn icon color="gray" @click="editRow(item)">
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn icon color="gray" @click="confirmDelete(item.id)">
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </td>
              <td v-for="header in columns" :key="header.value">
                {{ item[header.value] }}
              </td>
            </tr>
          </template>


      </v-data-table>
      
    </v-card>


    <!-- <h3>format table: {{ format_table }}</h3>
    <h3> Columns: {{ columns }}</h3> -->
    <h3>serverSide: {{option_table.serverSide}}</h3>
  </div>

  
</template>
  
  
  
  
  
  
  
<script>

  import { copy, sortDate } from "@/core/js/util/util.js";
  import { apiRequest, url } from "@/core/js/data/api.js";
  import {ref, onMounted} from "vue";
  import "./table.css";

  // import formRealisation from "../form/formRealisation.vue";   
  // import { sortDate } from "./util.js"; // remis dans js/util/util.js car c'était un doublon
  // import genericForm from "@/components/form/generic-form";




  const PARAMS_REQUETE = ref({
    page: 1, // page de démarrage ou page courante
    itemsPerPage: 10,
    sortBy: ["nom_saison", "date_exacte"], // utilisé la valeur de fields dans format_table
    sortDesc: [true,true], // un tableau de booléens pour chaque elements de sortBy
    fields: [], // sera rempli par la fonction build_param_requete_Fields à partir de format_table
    
  });
  

  const OPTIONS_TABLE = ref({
    title: "Données chasse",
    style: {
            "small-table": true, // typo taille réduite
            "striped": true, // une ligne grisée sur 2
            },
    serverSide: true,
    dense: true,
    itemsPerPage: 10,

  });

  // indiquer de nom à afficher en titre de colonne et le nom du champs
  // par defaut, visible=true,
  // noSearch=false : Si true, retire le champ de recherche au dessus de la colonne
  const FORMAT_TABLE = ref([
    { title: "Actions", fields:"id_realisation"},
    { title: "Saison", fields:"saison.nom_saison" },
    { title: "Bracelet", fields:"attribution.numero_bracelet" },
    { title: "Date de tir", fields:"date_exacte" },
    { title: "Auteur constat", fields:"auteur_constat.nom_personne" },
    { title: "Auteur tir", fields:"auteur_tir.nom_personne" },
    { title: "ZC realisée", fields:"zone_cynegetique_realisee.nom_zone_cynegetique" },
    { title: "ZI réalisée", fields:"zone_indicative_realisee.nom_zone_indicative" },
    { title: "Lieu tir synonyme", fields:"lieu_tir_synonyme.lieu_tir_synonyme_display" },
    { title: "Sexe", fields:"nomenclature_sexe.label_fr" },
    { title: "Classe d'age", fields:"nomenclature_classe_age.label_fr" },
    { title: "Mode chasse", fields:"nomenclature_mode_chasse.label_fr" }
    ])

    
    // quelques fonctions utilitaires
  const getNestedValue = (obj, path) => {
        return path.split('.').reduce((acc, part) => acc && acc[part], obj) || 'N/A';
    };



  export default {
    name: "tableChasse",
    
    data: () => ({
      options: {},
      configTable: {},
      searchs: {},
      saveValue: null,
      msgError: null,
      bError: false,
      idToDelete: null,
      deleteModal: null,
      deleteWithoutWarning: false,
      configForm: null,
      bEditDialog: false,
      itemsServerCount: null,
      url_requete: null,
      param_requete: PARAMS_REQUETE,
      option_table: OPTIONS_TABLE,
      columns: [],
      format_table: FORMAT_TABLE,
      items: [],

      responseData: {
        items: [], // Ici, les données seront chargées
        total: 0,
        total_filtered: 0
      }

    }),


    watch: {
      config: {
        handler() {
          this.initConfig();
        },
        deep: true
      },

      searchs: {
        handler() {
          this.loadData(false);
        },
        deep: true
      },
  
      options() {
        this.loadData(false);
      }
    },


    methods: {

      // Rempli le param_requete avec les champs indiqué dans format_table pour constuire la requête
      build_param_requete_Fields() {
        const selectedFields = this.format_table.map(item => item.fields).join(",");
        
        this.param_requete = {
          ...this.param_requete,
          fields: selectedFields
        };
        return this.param_requete;
      },

      async fetchData() {
        try {
          const response = await fetch(this.url_requete ); // Remplace avec ton endpoint
          const data = await response.json();
          this.responseData = data;
        } catch (error) {
          console.error("Erreur lors du chargement des données", error);
        }
      },

      build_dataTable() {
        
        // Met la valeur par défaut de visible à true si elle n'est pas définie
        this.format_table.map(item => {
          if (item.visible === undefined) {
            item.visible = true; 
          }
        });

        // On construit les colonnes pour le tableau
        this.columns = this.format_table.map(item => ({
          title: item.title, // semble etre "title" à la place de "text" sur la dernière version vuetify. Du coup on met les deux
          text: item.title,
          key: item.fields, // besoin de key à la place de value dans la dernière version de vuetify
          value: item.fields,
          visible: item.visible, // visible par défaut

        })).filter(item => item.visible); // On ne garde que les colonnes visibles
      },

      init_table(){
        // cette fonction est appelée dans le mounted pour initialiser le tableau
        // creation d'une requete pour récupèrer la première page
        // construction de columns et format_table pour afficher le tableau selon le format v-data-table

        this.param_requete = this.build_param_requete_Fields();
        this.url_requete = url("api/generic/chasse/realisations/", this.param_requete);
        this.fetchData(); // le resultat est stocké dans responseData

        this.build_dataTable();

      },

      loadData(loaded) {
      /** call preloadData */
      if (this.configTable.preloadData && !loaded) {
        this.configTable.preloadData({ $store: this.$store }).then(
          res => {
            for (const [index, key] of Object.keys(
              this.configTable.stores
            ).entries()) {
              if (key == "items") {
                let items = res[index];

                // sortie du
                if (items && items.items) {
                  this.itemsServerCount = items.total_filtered;
                  items = items.items;
                } else if (items) {
                  this.itemsServerCount = items.length;
                }

                if (items) {
                  this.configTable.items = this.configTable.preProcess
                    ? this.configTable.preProcess({ data: items })
                    : items;
                }
              }
            }
            this.configTable.loaded = true;
            this.configTable = copy(this.configTable);
          },
          error => {
            this.msgError = error;
            this.bError = true;
          }
        );
      }
    }

    },


    computed: {

      mappedItems() {
        return this.responseData.items.map(item => {
          const mappedItem = {};
          this.columns.forEach(column => {
            mappedItem[column.key] = getNestedValue(item, column.key);
          });
          return mappedItem;
        });
      },


    },


    initConfig() {
      const config = copy(this.config);
      config.loaded = false;
      config.stores = {};

      if (config.storeName) {
        const configStore = this.$store.getters.configStore(config.storeName);
        config.serverSide = configStore.serverSide;
        config.idFieldName = configStore.idFieldName;
        this.options = {
          ...this.options,
          ...(configStore.options || {})
        };
        config.displayFieldName =
          config.displayFieldName || configStore.displayFieldName;
        config.delete = (id, { $store }) => {
          return $store.dispatch(configStore.delete, { value: id });
        };

        config.stores.items = config.storeName;


        if (!config.headerDefs.actions) {
          config.headerDefs.actions = {
            noSearch: true,
            width: "90px",
            text: "Actions",
            sortable: false,
            edit: config.configForm,
            list: [
              {
                title: "Editer la ligne",
                icon: "mdi-pencil",
                click: id => this.edit("actions", id)
              },
              {
                title: "Supprimer la ligne",
                icon: "mdi-trash-can",
                click: id => {
                  if (!this.deleteWithoutWarning) {
                    this.idToDelete = id;
                    this.deleteModal = true;
                  } else {
                    this.deleteRow(id);
                  }
                }
              }
            ]
          };
        }

      }
      /** contruction de la variable header */
      const headers = [];

      for (const [value, header] of Object.entries(config.headerDefs)) {
        header.value = value;
        
        if (header.type == "date") {
          sortDate; // apparemment inutilisé
          header.display = a =>
            a && a[header.value] && a[header.value].includes("-")
              ? a[header.value]
                  .split("-")
                  .reverse()
                  .join("/")
              : a[header.value];
        }

        if (header.storeName) {
          const configStore = this.$store.getters.configStore(header.storeName);
          header.displayFieldName =
            header.displayFieldName || configStore.displayFieldName;

          /** test pour ne pas avoir deux fois le même store name */
          if (!Object.values(config.stores).includes(header.storeName)) {
            // config.stores[value] = header.storeName;
          }
          if (header.displayFieldName) {
            // on change ça
            header.display = d => {
              if (!d) {
                return "";
              }

              // case secteur.nom_secteur
              const displayFieldNames = header.displayFieldName.split(".");

              let inter = d[header.value];
              if (!inter) {
                return "";
              }
              return displayFieldNames.map(key => inter[key]).join(" ");
            };
          }
          header.sort = (a, b) => {
            const aa = header.display
              ? header.display(a, { $store: this.$store })
              : a;
            const bb = header.display
              ? header.display(b, { $store: this.$store })
              : b;
            return aa == bb ? 0 : aa < bb ? -1 : 1;
          };
        }
        if (!header.condition || header.condition({ $store: this.$store })) {
          headers.push(header);
        }
      }

      /** on place actions en début de liste */
      const headerActionsIndex = headers.findIndex(h => h.value === "actions");
      if (headerActionsIndex != -1) {
        const headerActions = headers[headerActionsIndex];
        headers.splice(headerActionsIndex, 1);
        headers.unshift(headerActions);
      }

      config.headers = headers;

      config.classes = {
        "small-table": config.small,
        striped: config.striped
      };

      /** preloadData with promises from storeNames */
      if (Object.keys(config.stores).length) {
        config.preloadData = ({ $store }) => {
          const promises = [];
          for (const storeName of Object.values(config.stores)) {
            const configStore = this.$store.getters.configStore(storeName);

            // on ajoute __like apres les clés de filtres
            // pour pouvoir filtrer en ilike ensuite
            const searchOptions = {};
            for (const [keySearch, valueSearch] of Object.entries(
              this.searchs || {}
            )) {
              const header = this.configTable.headers.find(h => h.value === keySearch)
              let key = header.displayFieldName ? `${keySearch}.${header.displayFieldName}` : keySearch
              searchOptions[`${key}__ilike`] = valueSearch;
            }

            // on change les clé de tri pour les storeName
            const sortBy = [...this.options.sortBy]
            for (const [index, keySort] of this.options.sortBy.entries()) {
              const header = this.configTable.headers.find(h => h.value === keySort)
              if (header.displayFieldName) {
                sortBy[index] = `${this.options.sortBy[index]}.${header.displayFieldName}`;
              }
            }

            const options =
              storeName == config.storeName && configStore.serverSide
                ? {
                    ...this.options,
                    notCommit: true,
                    ...searchOptions,
                    sortBy,
                    serverSide: true
                  }
                : {};
            promises.push($store.dispatch(configStore.getAll, options));
          }
          return Promise.all(promises);
        };
      }

      /** preProcess from headerDefs */
      if (config.headers.some(h => h.preProcess)) {
        config.preProcess = ({ data }) => {
          return data.map(d => {
            for (const header of this.configTable.headers.filter(
              h => h.preProcess
            )) {
              d[header.value] = header.preProcess(d);
            }
            return d;
          });
        };
      }

      this.configTable = config;
      this.loadData(this.configTable.loaded);
    },




    mounted() {
      // this.url_test = url("api/generic/chasse/realisations/", this.param_url )
      // this.fetchData();
      this.init_table();

    }
  };

  </script>
  

