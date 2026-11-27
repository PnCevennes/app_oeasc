<!--
  Page d'administration « Gestion des lieux de tirs » (visualisation).
  Gauche : filtres (commune, zone cynégétique, zone indicative, recherche) et liste des lieux de tir,
  chacun avec une case à cocher (décochée par défaut) qui affiche le lieu sur la carte.
  Droite : carte ; le contour de la commune / zone indicative / zone cynégétique filtrée s'affiche aussi.
  Un clic sur un lieu de la carte ouvre un encart avec ses informations et ses synonymes.
-->
<template>
  <div class="page-lieux-tir">
    <h1>Gestion des lieux de tirs</h1>

    <v-progress-linear
      v-if="loading"
      indeterminate
    ></v-progress-linear>

    <v-row>
      <v-col
        cols="12"
        md="4"
        lg="3"
        class="colonne-liste"
      >
        <!-- formulaire de modification (remplace filtres et liste) -->
        <div v-if="edition">
          <h3 class="mb-3">Modifier le lieu de tir</h3>
          <v-text-field
            v-model="edition.nom_lieu_tir"
            label="Nom *"
            density="compact"
            hide-details="auto"
            :rules="[(v) => !!(v && v.trim()) || 'Le nom est obligatoire']"
            class="mb-2"
          ></v-text-field>
          <v-text-field
            v-model="edition.code_lieu_tir"
            label="Code"
            density="compact"
            hide-details
            class="mb-2"
          ></v-text-field>
          <v-autocomplete
            v-model="edition.id_zone_indicative"
            :items="zonesIndicatives"
            item-title="nom"
            item-value="id"
            label="Zone indicative"
            density="compact"
            clearable
            hide-details
            class="mb-2"
          ></v-autocomplete>
          <v-combobox
            v-model="edition.synonymes"
            label="Synonymes (Entrée pour ajouter)"
            multiple
            chips
            closable-chips
            density="compact"
            hide-details
            class="mb-2"
          ></v-combobox>
          <div
            class="text-body-2 mb-2"
            :class="{ 'text-error': !edition.points.length }"
          >
            {{ edition.points.length }} point(s). Sur la carte : clic = ajouter, glisser =
            déplacer, clic droit ou double-clic sur un point = supprimer.
          </div>
          <div class="d-flex">
            <v-btn
              variant="text"
              :disabled="enregistrement"
              @click="annulerEdition"
            >
              Annuler
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              :loading="enregistrement"
              :disabled="!edition.nom_lieu_tir || !edition.nom_lieu_tir.trim() || !edition.points.length"
              @click="enregistrer"
            >
              Enregistrer
            </v-btn>
          </div>
        </div>

        <template v-else>
        <v-autocomplete
          v-model="idCommune"
          :items="communes"
          item-title="nom"
          item-value="id"
          label="Commune"
          density="compact"
          clearable
          hide-details
          class="mb-2"
        ></v-autocomplete>
        <v-autocomplete
          v-model="idZoneCynegetique"
          :items="zonesCynegetiques"
          item-title="nom"
          item-value="id"
          label="Zone cynégétique"
          density="compact"
          clearable
          hide-details
          class="mb-2"
        ></v-autocomplete>
        <v-autocomplete
          v-model="idZoneIndicative"
          :items="zonesIndicativesDisponibles"
          item-title="nom"
          item-value="id"
          label="Zone indicative"
          density="compact"
          clearable
          hide-details
          class="mb-2"
        ></v-autocomplete>
        <v-text-field
          v-model="recherche"
          label="Rechercher (nom, code, synonyme)"
          density="compact"
          clearable
          hide-details
          prepend-inner-icon="mdi-magnify"
          class="mb-2"
        ></v-text-field>

        <div class="d-flex align-center mb-1">
          <span class="text-body-2">
            {{ lieuxFiltres.length }} lieu(x) · {{ nbCoches }} affiché(s)
          </span>
          <v-spacer></v-spacer>
          <v-btn
            size="x-small"
            variant="text"
            @click="cocherFiltres(true)"
          >
            Tout cocher
          </v-btn>
          <v-btn
            size="x-small"
            variant="text"
            @click="cocherFiltres(false)"
          >
            Tout décocher
          </v-btn>
          <v-btn
            icon="mdi-close-box-multiple-outline"
            size="x-small"
            variant="text"
            title="Désélectionner tous les lieux, y compris hors filtres"
            :disabled="!coches.size"
            @click="toutDeselectionner"
          ></v-btn>
        </div>

        <div class="liste-lieux">
          <div
            v-for="lieu of lieuxFiltres"
            :key="lieu.properties.id_lieu_tir"
            class="ligne-lieu"
          >
            <v-checkbox-btn
              class="case-lieu"
              :model-value="coches.has(lieu.properties.id_lieu_tir)"
              density="compact"
              @update:model-value="cocher(lieu.properties.id_lieu_tir, $event)"
            ></v-checkbox-btn>
            <div
              class="texte-lieu"
              @click="activer(lieu.properties.id_lieu_tir)"
            >
              <div class="nom-lieu">{{ lieu.properties.nom_lieu_tir }}</div>
              <div class="detail-lieu">
                {{ lieu.properties.nom_commune }}
                <template v-if="lieu.properties.nom_zone_indicative">
                  · {{ lieu.properties.nom_zone_indicative }}
                </template>
              </div>
              <div
                v-if="lieu.properties.synonymes.length"
                class="detail-lieu"
              >
                Synonymes : {{ lieu.properties.synonymes.join(', ') }}
              </div>
            </div>
            <div class="actions-lieu">
              <v-btn
                icon="mdi-pencil"
                size="x-small"
                variant="text"
                title="Modifier"
                @click="commencerEdition(lieu)"
              ></v-btn>
              <v-btn
                icon="mdi-delete"
                size="x-small"
                variant="text"
                color="error"
                title="Supprimer"
                @click="lieuASupprimer = lieu"
              ></v-btn>
            </div>
          </div>
          <div
            v-if="!loading && !lieuxFiltres.length"
            class="detail-lieu pa-2"
          >
            Aucun lieu de tir pour ces filtres.
          </div>
        </div>
        </template>
      </v-col>

      <v-col
        cols="12"
        md="8"
        lg="9"
      >
        <map-lieux-tir
          ref="carte"
          :edition="edition ? { points: edition.points } : null"
          @update:points="edition.points = $event"
          :lieux="lieuxCoches"
          :contours="contours"
          :lieu-actif="lieuActif"
        ></map-lieux-tir>
        <div class="legende">
          <span class="legende-item">
            <span
              class="legende-point"
              style="background: #e53935"
            ></span>
            Lieu de tir
          </span>
          <span class="legende-item">
            <span
              class="legende-zone"
              style="background: rgba(229, 57, 53, 0.2); border: 2px solid #e53935"
            ></span>
            Enveloppe (zone tampon de 1-2 points, polygone au-delà)
          </span>
          <span
            v-if="idCommune"
            class="legende-item"
          >
            <span
              class="legende-trait"
              style="background: #1e88ff"
            ></span>
            Commune
          </span>
          <span
            v-if="idZoneIndicative"
            class="legende-item"
          >
            <span
              class="legende-trait"
              style="background: #e53935"
            ></span>
            Zone indicative
          </span>
          <span
            v-if="idZoneCynegetique"
            class="legende-item"
          >
            <span
              class="legende-trait"
              style="background: #000000"
            ></span>
            Zone cynégétique
          </span>
        </div>
      </v-col>
    </v-row>

    <v-dialog
      :model-value="!!lieuASupprimer"
      max-width="500"
      @update:model-value="lieuASupprimer = null"
    >
      <v-card v-if="lieuASupprimer">
        <v-card-title>Supprimer ce lieu de tir ?</v-card-title>
        <v-card-text>
          Le lieu « {{ lieuASupprimer.properties.nom_lieu_tir }} » sera supprimé définitivement
          <template v-if="lieuASupprimer.properties.synonymes.length">
            ainsi que ses {{ lieuASupprimer.properties.synonymes.length }} synonyme(s) :
            {{ lieuASupprimer.properties.synonymes.join(', ') }}.
          </template>
          <template v-else>.</template>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            :disabled="suppression"
            @click="lieuASupprimer = null"
          >
            Annuler
          </v-btn>
          <v-btn
            color="error"
            variant="text"
            :loading="suppression"
            @click="supprimer"
          >
            Supprimer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { apiRequest } from '@/core/js/data/api.js';
import { snackbarStore } from '@/store/snackbar';
import { describeApiError } from '@/core/js/data/api-messages.js';
import MapLieuxTir from './map/map-lieux-tir.vue';

// normalise pour une recherche insensible à la casse et aux accents
const norm = (texte) =>
  String(texte ?? '')
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase();

export default {
  name: 'LieuxTirChasse',
  components: { MapLieuxTir },
  data: () => ({
    loading: false,
    lieux: [], // toutes les Features
    communes: [],
    zonesIndicatives: [],
    zonesCynegetiques: [],
    idCommune: null,
    idZoneCynegetique: null,
    idZoneIndicative: null,
    recherche: '',
    coches: new Set(), // id_lieu_tir cochés (aucun par défaut)
    lieuActif: null,
    // contours chargés, en cache : clé "type:id" -> Feature
    cacheContours: {},
    contours: [],
    edition: null, // lieu en cours de modification (copie de travail) ou null
    enregistrement: false,
    lieuASupprimer: null, // Feature dont la suppression attend confirmation
    suppression: false,
  }),
  computed: {
    // la liste des zones indicatives suit la zone cynégétique choisie
    zonesIndicativesDisponibles() {
      return this.idZoneCynegetique
        ? this.zonesIndicatives.filter((z) => z.id_zone_cynegetique === this.idZoneCynegetique)
        : this.zonesIndicatives;
    },
    lieuxFiltres() {
      const texte = norm(this.recherche);
      return this.lieux.filter((f) => {
        const p = f.properties;
        if (this.idCommune && p.id_area_commune !== this.idCommune) return false;
        if (this.idZoneCynegetique && p.id_zone_cynegetique !== this.idZoneCynegetique) return false;
        if (this.idZoneIndicative && p.id_zone_indicative !== this.idZoneIndicative) return false;
        if (!texte) return true;
        return [p.nom_lieu_tir, p.code_lieu_tir, ...p.synonymes].some((s) =>
          norm(s).includes(texte)
        );
      });
    },
    // la carte n'affiche que les lieux cochés ET conformes aux filtres actifs
    lieuxCoches() {
      return this.lieuxFiltres.filter((f) => this.coches.has(f.properties.id_lieu_tir));
    },
    nbCoches() {
      return this.lieuxCoches.length;
    },
  },
  watch: {
    idCommune() {
      this.majContours();
    },
    idZoneCynegetique(id) {
      // une zone indicative d'une autre zone cynégétique n'a plus de sens
      const zi = this.zonesIndicatives.find((z) => z.id === this.idZoneIndicative);
      if (id && zi && zi.id_zone_cynegetique !== id) {
        this.idZoneIndicative = null;
      }
      this.majContours();
    },
    idZoneIndicative(id) {
      // choisir une zone indicative renseigne sa zone cynégétique
      const zi = this.zonesIndicatives.find((z) => z.id === id);
      if (zi && zi.id_zone_cynegetique && !this.idZoneCynegetique) {
        this.idZoneCynegetique = zi.id_zone_cynegetique;
      }
      this.majContours();
    },
  },
  methods: {
    async charger() {
      this.loading = true;
      try {
        const res = await apiRequest('GET', 'api/chasse/lieux-tir/carte');
        this.lieux = res.lieux.features;
        this.communes = res.communes;
        this.zonesIndicatives = res.zones_indicatives;
        this.zonesCynegetiques = res.zones_cynegetiques;
        this.coches = new Set([...this.coches].filter((id) => res.lieux.features.some((f) => f.properties.id_lieu_tir === id)));
      } catch (error) {
        console.error(error);
        snackbarStore.show('Impossible de charger les lieux de tir.', 'error');
      } finally {
        this.loading = false;
      }
    },

    // Set recréé à chaque changement pour déclencher la réactivité
    cocher(id, valeur) {
      const coches = new Set(this.coches);
      if (valeur) {
        coches.add(id);
      } else {
        coches.delete(id);
      }
      this.coches = coches;
    },
    cocherFiltres(valeur) {
      const coches = new Set(this.coches);
      for (const f of this.lieuxFiltres) {
        if (valeur) {
          coches.add(f.properties.id_lieu_tir);
        } else {
          coches.delete(f.properties.id_lieu_tir);
        }
      }
      this.coches = coches;
    },
    // décoche tous les lieux, même ceux masqués par les filtres
    toutDeselectionner() {
      this.coches = new Set();
      this.lieuActif = null;
    },
    // clic sur un lieu de la liste : le coche si besoin et ouvre son encart
    activer(id) {
      if (!this.coches.has(id)) {
        this.cocher(id, true);
      }
      this.lieuActif = null;
      this.$nextTick(() => {
        this.lieuActif = id;
      });
    },

    commencerEdition(lieu) {
      const p = lieu.properties;
      this.lieuActif = null;
      this.edition = {
        id_lieu_tir: p.id_lieu_tir,
        nom_lieu_tir: p.nom_lieu_tir,
        code_lieu_tir: p.code_lieu_tir,
        id_zone_indicative: p.id_zone_indicative,
        synonymes: [...p.synonymes],
        points: lieu.geometry.coordinates.map((c) => [...c]),
      };
      this.$nextTick(() => this.$refs.carte.cadrerEdition());
    },
    annulerEdition() {
      this.edition = null;
    },
    async enregistrer() {
      const e = this.edition;
      this.enregistrement = true;
      try {
        await apiRequest('PATCH', `api/chasse/lieux-tir/${e.id_lieu_tir}`, {
          postData: {
            nom_lieu_tir: e.nom_lieu_tir,
            code_lieu_tir: e.code_lieu_tir,
            id_zone_indicative: e.id_zone_indicative,
            synonymes: e.synonymes,
            geometry: { type: 'MultiPoint', coordinates: e.points },
          },
        });
        this.edition = null;
        await this.charger();
        this.cocher(e.id_lieu_tir, true);
        snackbarStore.show('Lieu de tir enregistré.', 'success');
      } catch (error) {
        console.error(error);
        snackbarStore.show(describeApiError(error), 'error');
      } finally {
        this.enregistrement = false;
      }
    },
    async supprimer() {
      const id = this.lieuASupprimer.properties.id_lieu_tir;
      this.suppression = true;
      try {
        await apiRequest('DELETE', `api/chasse/lieux-tir/${id}`);
        this.lieuASupprimer = null;
        this.cocher(id, false);
        await this.charger();
        snackbarStore.show('Lieu de tir supprimé.', 'success');
      } catch (error) {
        console.error(error);
        snackbarStore.show(describeApiError(error), 'error');
      } finally {
        this.suppression = false;
      }
    },

    async contour(type, id) {
      const cle = `${type}:${id}`;
      if (!this.cacheContours[cle]) {
        const res = await apiRequest('GET', 'api/chasse/lieux-tir/contour', {
          params: { type, id },
        });
        this.cacheContours[cle] = res.contour;
      }
      return this.cacheContours[cle];
    },
    // contours des filtres actifs (commune, zone indicative, zone cynégétique)
    async majContours() {
      const demandes = [
        ['commune', this.idCommune],
        ['zone_cynegetique', this.idZoneCynegetique],
        ['zone_indicative', this.idZoneIndicative],
      ].filter(([, id]) => id);
      const version = (this.versionContours = (this.versionContours || 0) + 1);
      try {
        const contours = await Promise.all(demandes.map(([type, id]) => this.contour(type, id)));
        // une demande plus récente a pu être lancée entre-temps
        if (version === this.versionContours) {
          this.contours = contours;
        }
      } catch (error) {
        console.error(error);
        snackbarStore.show('Impossible de charger le contour demandé.', 'error');
      }
    },
  },
  mounted() {
    this.charger();
  },
};
</script>

<style scoped>
/* largeur de la colonne indépendante du contenu (noms longs, valeurs des filtres, liste vide) */
.colonne-liste {
  min-width: 0;
  overflow-wrap: anywhere;
}
.page-lieux-tir {
  /* .main-container est un flex centré : sans largeur explicite, la page prend la largeur de son
     contenu et se rétrécit quand le filtre réduit la liste */
  width: 100%;
  padding: 0 40px 16px;
}
.liste-lieux {
  max-height: 520px;
  overflow-y: auto;
  overflow-x: hidden;
  border: 1px solid rgba(128, 128, 128, 0.4);
  border-radius: 4px;
}
.ligne-lieu {
  display: flex;
  align-items: flex-start;
  border-bottom: 1px solid rgba(128, 128, 128, 0.2);
  padding: 2px 4px;
}
.case-lieu {
  /* par défaut la case est extensible (flex: 1 0) et se partage la ligne avec le texte :
     le texte était décalé à droite selon sa longueur */
  flex: 0 0 auto;
}
.actions-lieu {
  flex: 0 0 auto;
  display: flex;
}
.texte-lieu {
  flex: 1 1 0;
  cursor: pointer;
  padding-top: 6px;
  min-width: 0;
}
.nom-lieu {
  font-weight: 500;
}
.detail-lieu {
  font-size: 0.8rem;
  opacity: 0.75;
}
.legende {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 6px;
  font-size: 0.85rem;
}
.legende-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.legende-point {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 1px #888;
}
.legende-zone {
  width: 18px;
  height: 12px;
}
.legende-trait {
  width: 22px;
  height: 3px;
}
</style>
