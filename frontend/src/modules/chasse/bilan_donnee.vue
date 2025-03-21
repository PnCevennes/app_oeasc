<div>
    <generic-form
    :config="{
        ...$store.getters.configFormContentChasse(['id_saison', 'id_espece', 'id_secteur', 'id_zone_cynegetique', 'id_zone_indicative']),
        value: contentValues
    }"
    ></generic-form>
</div>

<div>
    <graph-chasse
        v-bind=contentValues
        type='bilan'
    >
    </graph-chasse>
</div>

<div>
    <graph-chasse
        v-bind=contentValues
    :poids_ou_dagues="true"
        type='ice'
    >
    </graph-chasse>
</div>

<div>
    <graph-chasse v-bind=contentValues :poids_ou_dagues="true" type='ice_data'>
    </graph-chasse>
</div>

<div  v-if="contentValues.id_espece == 1">
<div>
<graph-chasse
    v-bind=contentValues
:poids_ou_dagues="false"
    type='ice'
>
</graph-chasse>
</div>

<div>
<graph-chasse
    v-bind=contentValues
:poids_ou_dagues="false"
    type='ice_data'
>
</graph-chasse>
</div>