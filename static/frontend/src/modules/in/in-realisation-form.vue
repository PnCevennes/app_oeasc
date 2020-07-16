<template>
  <div v-if="config">
    <generic-form :config="config"> </generic-form>
  </div>
</template>

<script>
import genericForm from "@/components/form/generic-form";

export default {
  name: "in-form",
  computed: {
    idRealisation() {
      return this.$route.params.idRealisation;
    },
    config() {
      return {
        preLoadData: () => {
          return new Promise(resolve => {
            if (!this.idRealisation) {
              resolve();
            }
            this.$store
              .dispatch("in_realisation", this.idRealisation)
              .then(data => {
                console.log(data);
                this.config.value = data;
                resolve();
              });
          });
        },

        switchDisplay: this.idRealisation,
        // value: {},
        // value: {
        //   observations: [{ espece: "Cerf", nb: 12 }],
        //   date_realisation: "2020-06-03",
        //   id_circuit: 1,
        //   observers: ["Jean", "Jack"],
        //   temperature: "Froid",
        //   vent: "Faible",
        //   temps: "Brouillard"
        // },
        groups: {
          informations: {
            title: "Informations",
            forms: {
              date_realisation: {
                type: "date",
                label: "Date",
                required: true
              },
              id_circuit: {
                type: "list_form",
                label: "Circuit",
                url: "api/in/circuits/",
                valueFieldName: "id_circuit",
                textFieldName: "label",
                display: "autocomplete",
                required: true
              },
              observers: {
                type: "list_form",
                display: "combobox",
                label: "Observateurs",
                maxLength: 4,
                multiple: true,
                url: "api/in/observers/",
                valueFieldName: "observer",
                textFieldName: "observer"
              }
            }
          },
          meteo: {
            title: "Météo",
            direction: "row",
            forms: {
              temperature: {
                label: "Température",
                type: "list_form",
                display: "select",
                items: ["Froid", "Frais", "Doux", "Chaud"]
              },
              temps: {
                label: "Temps",
                type: "list_form",
                display: "select",
                items: ["Sec", "Puie fine", "Brouillard", "Neige"]
              },
              vent: {
                label: "Vent",
                type: "list_form",
                display: "select",
                items: ["Nul", "Faible", "Moyen", "Fort"]
              }
            }
          },
          observations: {
            forms: {
              observations: {
                type: "list",
                label: "Observations",
                forms: {
                  espece: {
                    type: "list_form",
                    display: "combobox",

                    label: "Espece",
                    items: ["Cerf", "Chevreuil", "Renard", "Lièvre"],
                    required: true
                  },
                  nb: {
                    type: "number",
                    label: "Nombre d'individus",
                    min: 0,
                    required: true
                  },
                  id_observation: {
                    label: 'ID observation',
                    type: 'text',
                    hidden: true,
                  },
                }
              }
            }
          }
        },
        request: {
          url: `api/in/realisation/${this.idRealisation || ""}`,
          method: `${this.idRealisation ? "PATCH" : "POST"}`,
          onSuccess: (data) => {
            console.log('success', data)
          }
        }
      };
    }
  },
  data: function() {
    return {};
  },
  components: {
    genericForm
  }
};
</script>
