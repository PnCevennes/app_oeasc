<template>
    <div>
    <div class="small-table"></div>
    <v-simple-table dense class="small-table"  id="contacts">
      <col width="30%">
      <col width="20%">
      <col width="15%">
      <col width="25%">
      <thead class="thead-light">

        <tr>
          <th scope="col">Structure</th>
          <th scope="col">Nom</th>
          <th scope="col">Téléphone</th>
          <th scope="col">E-mail</th>
        </tr>

      </thead>

      <tbody>

        <tr>
          <td>Établissement public du Parc national des Cévennes</td>
          <td>ALGOËT Baptiste</td>
          <td>04 66 49 53 60</td>
          <td><a href="mailto:baptiste.algoet@cevennes-parcnational.fr">baptiste.algoet@cevennes-parcnational.fr</a></td>
        </tr>

        <tr>
          <td>CRPF Occitanie</td>
          <td>MOLINES Loïc</td>
          <td>06 73 84 89 27</td>
          <td><a href="mailto:loic.molines@crpf.fr">loic.molines@crpf.fr</a></td>
        </tr>

        <tr>
          <td>Syndicat lozérien de la forêt privée</td>
          <td>PIT Denis</td>
          <td>06 07 35 21 06</td>
          <td><a href="mailto:pit.denis@wanadoo.fr">pit.denis@wanadoo.fr</a></td>
        </tr>

        <tr>
          <td>Syndicat des forestiers privés du Gard</td>
          <td>CORRE Isabelle</td>
          <td>06 08 16 63 59</td>
          <td><a href="mailto:isa.corre83@gmail.com">isa.corre83@gmail.com</a></td>
        </tr>

        <tr>
          <td>Coopérative "La forêt privée lozérienne et gardoise"</td>
          <td>Secrétariat</td>
          <td>04 66 65 39 69</td>
          <td><a href="mailto:contact@fplg.fr">contact@fplg.fr</a></td>
        </tr>

        <tr>
          <td>Chambre d'agriculture de la Lozère</td>
          <td>JAUVERT Frédéric</td>
          <td>04 66 65 62 00</td>
          <td><a href="mailto:frederic.jauvert@lozere.chambagri.fr">frederic.jauvert@lozere.chambagri.fr</a></td>
        </tr>

      </tbody>

    </v-simple-table>
</div>

</template>

<script>
export default {
    name: "tableAide",  
}
</script>

<style scoped>
    .small-table td{
        font-size: 0.9em;
    }
</style>
