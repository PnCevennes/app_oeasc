"""
Fonctions de traitement de données pour les déclarations
"""

from sqlalchemy import (
    select,
    func,
    cast,
    Float,
)

from oeasc.modules.oeasc.i_n.models import (
    TRealisations,
    TCircuits,
    TObservations,
)
from oeasc.modules.oeasc.commons.models import TSecteurs, TEspeces


def stmt_results():
    """
    requete pour récupérer les résultats des IN pour la page admin indice nocturne
    """

    stmt = (
        select(
            TObservations.id_observation,
            TObservations.nb,
            TRealisations.groupes,
            TRealisations.valide_ZC,
            TRealisations.valide_PNC,
            TRealisations.serie,
            func.to_char(TRealisations.date_realisation, "DD/MM/YYYY").label("date"),
            TCircuits.id_circuit,
            TCircuits.nom_circuit,
            TCircuits.numero_circuit,
            TCircuits.in_coeur,
            TSecteurs.nom_secteur,
            TCircuits.km,
            TSecteurs.nom_secteur.label(
                "ug"
            ),  # on devra le modifier par la suite pour différencier le causses gorgess coeur
            TEspeces.nom_espece,
            TRealisations.id_realisation,
            (cast(TObservations.nb, Float) / TCircuits.km).label("nbkm"),
            func.to_char(TRealisations.date_realisation, "YYYY").label("annee"),
        )
        .join(
            TRealisations, TRealisations.id_realisation == TObservations.id_realisation
        )
        .join(TCircuits, TCircuits.id_circuit == TRealisations.id_circuit)
        .join(
            TSecteurs, TSecteurs.id_secteur == TCircuits.id_secteur
        )  # à revoir pour éviter les doublons
        .join(TEspeces, TEspeces.id_espece == TObservations.id_espece)
        .order_by(
            TSecteurs.nom_secteur,  # Tri par secteur
            TCircuits.in_coeur,  # puis par circuit (cœur en premier)
            TRealisations.date_realisation.desc(),  # puis par date de réalisation (plus récent en premier)
            TEspeces.nom_espece,  # puis par espèce
            TRealisations.serie,  # puis par série
            TCircuits.numero_circuit,  # puis par numéro de circuit
        )
    )

    return stmt
