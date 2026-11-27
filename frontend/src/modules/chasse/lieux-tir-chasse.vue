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
          <div class="zones-calculees mb-3">
            <div class="text-caption">Calculées automatiquement à l'enregistrement :</div>
            <div
              v-for="z of ZONES_EDITION"
              :key="z.cle"
              class="d-flex align-center"
            >
              <span
                class="legende-trait mr-2"
                :style="`background: ${z.couleur}`"
              ></span>
              <span>
                {{ z.label }} :
                <b>{{ edition.zones && edition.zones[z.cle] ? edition.zones[z.cle].nom : 'aucune' }}</b>
              </span>
            </div>
          </div>
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
          :contours="edition ? contoursEdition : contours"
          :lieu-actif="lieuActif"
        ></map-lieux-tir>
        <div class="legende">
          <span class="legende-item">
            <span
              class="legende-zone"
              style="background: rgba(229, 57, 53, 0.2); border: 2px solid #e53935"
            ></span>
            Lieu de tir (zone tampon pour 1-2 points, polygone au-delà ; points visibles en modification)
          </span>
          <span
            v-if="idCommune || edition"
            class="legende-item"
          >
            <span
              class="legende-trait"
              style="background: #1e88ff"
            ></span>
            Commune
          </span>
          <span
            v-if="idZoneIndicative || edition"
            class="legende-item"
          >
            <span
              class="legende-trait"
              style="background: #e53935"
            ></span>
            Zone indicative
          </span>
          <span
            v-if="idZoneCynegetique || edition"
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
      <v-card
        v-if="lieuASupprimer"
        class="carte-suppression"
      >
        <v-card-title>Supprimer ce lieu de tir ?</v-card-title>
        <v-card-text>
          Le lieu « {{ lieuASupprimer.properties.nom_lieu_tir }} » sera supprimé définitivement
          <template v-if="lieuASupprimer.properties.synonymes.length">
            ainsi que ses {{ lieuASupprimer.properties.synonymes.length }} synonyme(s) :
            {{ lieuASupprimer.properties.synonymes.join(', ') }}.
          </template>
          <template v-else>.</template>
          <div class="mt-2">
            <template v-if="chargementRealisations">Recherche des réalisations…</template>
            <template v-else-if="realisationsLieu.length">
              <b>{{ realisationsLieu.length }} réalisation(s)</b> sont rattachées à ce lieu
              (<template
                v-for="(id, i) of realisationsLieu"
                :key="id"
                ><a
                  href="#"
                  title="Modifier la réalisation"
                  @click.prevent="ouvrirRealisation(id)"
                  >{{ id }}</a
                ><template v-if="i < realisationsLieu.length - 1">, </template></template
              >) : elles seront conservées mais n'auront plus de lieu de tir associé.
            </template>
            <template v-else>Aucune réalisation n'est rattachée à ce lieu.</template>
          </div>
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

    <!-- modification d'une réalisation rattachée au lieu à supprimer -->
    <v-dialog
      v-model="dialogRealisation"
      persistent
      max-width="1400px"
    >
      <v-card>
        <generic-form
          v-if="dialogRealisation && configRealisation"
          class="pa-4"
          :config="configRealisation"
        ></generic-form>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { apiRequest } from '@/core/js/data/api.js';
import { snackbarStore } from '@/store/snackbar';
import { describeApiError } from '@/core/js/data/api-messages.js';
import MapLieuxTir from './map/map-lieux-tir.vue';
import GenericForm from '@/components/form/generic-form.vue';

// normalise pour une recherche insensible à la casse et aux accents
const norm = (texte) =>
  String(texte ?? '')
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase();

export default {
  name: 'LieuxTirChasse',
  components: { MapLieuxTir, GenericForm },
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
    contoursEdition: [], // contours de la commune / ZI / ZC calculées pour les points édités
    ZONES_EDITION: [
      { cle: 'commune', type: 'commune', label: 'Commune', couleur: '#1e88ff' },
      { cle: 'zone_indicative', type: 'zone_indicative', label: 'Zone indicative', couleur: '#e53935' },
      { cle: 'zone_cynegetique', type: 'zone_cynegetique', label: 'Zone cynégétique', couleur: '#000000' },
    ],
    enregistrement: false,
    lieuASupprimer: null, // Feature dont la suppression attend confirmation
    suppression: false,
    realisationsLieu: [], // numéros des réalisations rattachées au lieu à supprimer
    chargementRealisations: false,
    dialogRealisation: false,
    configRealisation: null,
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
    // à l'ouverture de la confirmation de suppression : réalisations rattachées au lieu
    lieuASupprimer(lieu) {
      this.realisationsLieu = [];
      if (lieu) {
        this.chargerRealisations();
      }
    },
    // points modifiés : recalcul (temporisé) de la commune et des zones
    'edition.points': {
      deep: true,
      handler() {
        clearTimeout(this.minuteurZones);
        this.minuteurZones = setTimeout(() => this.calculerZones(), 300);
      },
    },
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
        zones: null, // commune / ZI / ZC calculées (voir calculerZones)
        synonymes: [...p.synonymes],
        points: lieu.geometry.coordinates.map((c) => [...c]),
      };
      this.$nextTick(() => this.$refs.carte.cadrerEdition());
      this.calculerZones();
    },
    annulerEdition() {
      clearTimeout(this.minuteurZones);
      this.edition = null;
      this.contoursEdition = [];
    },
    async calculerZones() {
      const e = this.edition;
      if (!e) {
        return;
      }
      const version = (this.versionZones = (this.versionZones || 0) + 1);
      try {
        const res = e.points.length
          ? await apiRequest('POST', 'api/chasse/lieux-tir/zones', {
              postData: { points: e.points },
            })
          : {};
        const zones = {
          commune: res.commune || null,
          zone_indicative: res.zone_indicative || null,
          zone_cynegetique: res.zone_cynegetique || null,
        };
        const contours = await Promise.all(
          this.ZONES_EDITION.filter((z) => zones[z.cle]).map((z) => this.contour(z.type, zones[z.cle].id))
        );
        // une demande plus récente a pu être lancée, ou l'édition fermée
        if (version === this.versionZones && this.edition === e) {
          e.zones = zones;
          this.contoursEdition = contours;
        }
      } catch (error) {
        console.error(error);
        snackbarStore.show(describeApiError(error), 'error');
      }
    },
    async enregistrer() {
      const e = this.edition;
      this.enregistrement = true;
      try {
        await apiRequest('PATCH', `api/chasse/lieux-tir/${e.id_lieu_tir}`, {
          postData: {
            nom_lieu_tir: e.nom_lieu_tir,
            code_lieu_tir: e.code_lieu_tir,
            synonymes: e.synonymes,
            geometry: { type: 'MultiPoint', coordinates: e.points },
          },
        });
        this.annulerEdition();
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
    async chargerRealisations() {
      const lieu = this.lieuASupprimer;
      if (!lieu) {
        return;
      }
      this.chargementRealisations = true;
      try {
        const res = await apiRequest(
          'GET',
          `api/chasse/lieux-tir/${lieu.properties.id_lieu_tir}/realisations`
        );
        // le lieu a pu changer pendant la requête
        if (this.lieuASupprimer === lieu) {
          this.realisationsLieu = res.realisations;
        }
      } catch (error) {
        console.error(error);
        snackbarStore.show(describeApiError(error), 'error');
      } finally {
        this.chargementRealisations = false;
      }
    },
    // ouvre le formulaire de modification de la réalisation (config recréée à chaque ouverture :
    // generic-form la modifie)
    ouvrirRealisation(id) {
      const fermer = () => {
        this.dialogRealisation = false;
        this.configRealisation = null;
        // le lieu de la réalisation a pu changer : on rafraîchit la liste
        this.chargerRealisations();
      };
      // copie de la config du store (avec formDefs : generic-form ne l'écrase alors pas), en mode
      // édition directe
      this.configRealisation = {
        ...this.$store.getters.configStore('chasseRealisation').configForm,
        switchDisplay: false,
        displayValue: false,
        value: { id_realisation: id },
        title: `Modifier la réalisation ${id}`,
        cancel: { action: fermer },
        action: { onSuccess: fermer },
      };
      this.dialogRealisation = true;
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
.carte-suppression a {
  cursor: pointer;
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
.legende-zone {
  width: 18px;
  height: 12px;
}
.legende-trait {
  width: 22px;
  height: 3px;
}
</style>
