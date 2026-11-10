"""convertit les <content-img> des contenus en images de l'éditeur visuel

Les contenus (oeasc_commons.t_contents.md) insèrent leurs images avec le composant Vue
`<content-img src=… center|float=… title=… source=… width=… link=… risetitle>`. L'éditeur visuel
(WYSIWYG, Tiptap) gère maintenant les mêmes options (position gauche / centre / droite /
flottante, légende, auteur, titre sur l'image, lien au clic, largeur en px) avec une image qui
produit le même HTML que le composant (div.img-content > figure > img + figcaption, styles de
content.css) : les images s'affichent dans le formulaire et se modifient directement.

Conversion :
  - le nom de fichier devient `:src="imgPath + 'nom.jpg'"` (imgPath = chemin des images du site,
    computed de content.vue) : aucun domaine n'est écrit dans le texte
  - float="left|right" -> flottante ; center -> centrée ; width (px) -> largeur
  - title -> légende, source -> auteur, link -> lien au clic, risetitle conservé
  - `height` est abandonné : combiné à la largeur à 100 % du composant il déformait l'image
  - une largeur en % n'est pas convertie (aucune dans les contenus au 2026-11-10)
  - un <content-img> sans `src` fixe (liaison Vue) ou à adresse complète est laissé tel quel
Des lignes vides sont ajoutées autour de l'image : un <div> en début de ligne ouvre un bloc HTML
en markdown, qui absorberait sinon le texte des lignes suivantes.

Seule la colonne md est modifiée (meta_update_date inchangée). downgrade : reconversion au mieux
(la position « droite » non flottante n'a pas d'équivalent : elle redevient flottante à droite).

Revision ID: 7d3f9a1c5e82
Revises: e5b7d3a91c24
Create Date: 2026-11-10 18:00:00.000000

"""

import html as _html
import re

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7d3f9a1c5e82"
down_revision = "e5b7d3a91c24"
branch_labels = None
depends_on = None


_IMG = re.compile(
    r"<content-img\b((?:\"[^\"]*\"|'[^']*'|[^>\"'])*)>(?:\s*</content-img\s*>)?", re.I
)
_ATTR = re.compile(r"""([^\s=/"'>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?""")
_ABSOLU = re.compile(r"^([a-z][a-z0-9+.-]*:|/|\.)", re.I)


def _attributs(brut):
    brut = brut.rstrip()
    if brut.endswith("/"):  # <content-img … />
        brut = brut[:-1]
    props = {}
    for m in _ATTR.finditer(brut):
        valeur = next((g for g in m.groups()[1:] if g is not None), "")
        props[m.group(1).lower()] = _html.unescape(valeur)
    return props


def _attr(valeur):
    return _html.escape(valeur, quote=True)


def _expr_chemin(nom):
    return "imgPath + '%s'" % nom.replace("\\", "\\\\").replace("'", "\\'")


def _largeur_px(valeur):
    m = re.fullmatch(r"\s*(\d+)(?:\.\d+)?\s*(?:px)?\s*", valeur or "")
    return int(m.group(1)) if m and int(m.group(1)) > 0 else None


def convertit_image(brut):
    """HTML de l'image de l'éditeur pour un <content-img> (attributs `brut`) ; None si impossible."""
    props = _attributs(brut)
    src = props.get("src", "").strip()
    if not src or _ABSOLU.match(src) or any(k.startswith((":", "v-", "@")) for k in props):
        return None

    if props.get("float") in ("left", "right"):
        alignement = "float-" + props["float"]
    elif "center" in props:
        alignement = "center"
    else:
        alignement = None
    positions = {
        "center": "center",
        "float-left": "float left",
        "float-right": "float right",
    }
    classes = ["img-content", "img-wysiwyg"]
    if alignement:
        classes += positions[alignement].split(" ")
    risetitle = "risetitle" in props
    if risetitle:
        classes.append("risetitle")

    titre, source, lien = props.get("title", ""), props.get("source", ""), props.get("link", "")
    largeur = _largeur_px(props.get("width"))
    # même titre d'image (infobulle / alt) que content-img.vue
    titre_img = ("%s %s" % (titre or src, source)).strip()

    img = '<img :src="%s" title="%s" alt="%s">' % (
        _attr(_expr_chemin(src)),
        _attr(titre_img),
        _attr(titre_img),
    )
    if lien:
        if _ABSOLU.match(lien):
            href = 'href="%s"' % _attr(lien)
        else:
            href = ':href="%s"' % _attr(_expr_chemin(lien))
        img = '<a %s target="_blank" rel="noopener noreferrer">%s</a>' % (href, img)
    legende = ""
    if titre or source:
        legende = '<figcaption><div class="img-text">%s%s</div></figcaption>' % (
            _html.escape(titre, quote=False),
            '<i class="source"> - %s</i>' % _html.escape(source, quote=False) if source else "",
        )

    attrs = ['class="%s"' % " ".join(classes)]
    if largeur:
        attrs.append('style="width:%dpx"' % largeur)
    attrs.append('data-img-wysiwyg="%s"' % _attr(src))
    if titre:
        attrs.append('data-titre="%s"' % _attr(titre))
    if source:
        attrs.append('data-source="%s"' % _attr(source))
    if lien:
        attrs.append('data-lien="%s"' % _attr(lien))
    if alignement:
        attrs.append('data-align="%s"' % alignement)
    if largeur:
        attrs.append('data-largeur="%d"' % largeur)
    if risetitle:
        attrs.append("data-risetitre")
    return "<div %s><figure>%s%s</figure></div>" % (" ".join(attrs), img, legende)


def convertit_contenu(md):
    """Remplace chaque <content-img> du texte, en entourant l'image de lignes vides."""

    def remplace(m):
        neuf = convertit_image(m.group(1))
        if neuf is None:
            return m.group(0)
        debut, fin = m.start(), m.end()
        debut_ligne = md.rfind("\n", 0, debut) + 1
        fin_ligne = md.find("\n", fin)
        fin_ligne = len(md) if fin_ligne == -1 else fin_ligne
        avant = md[debut_ligne:debut]
        apres = md[fin:fin_ligne]
        if avant.strip() == "" and apres.strip() == "":
            # seule sur sa ligne : ligne vide avant et après si ce n'est pas déjà le cas
            precedent = md[:debut_ligne]
            suivant = md[fin_ligne:]
            prefixe = "\n" if precedent and not precedent.endswith("\n\n") else ""
            suffixe = "\n" if suivant.startswith("\n") and not suivant.startswith("\n\n") and len(suivant) > 1 else ""
            return prefixe + neuf + suffixe
        if avant.strip() == "":
            return neuf + "\n\n"  # début de ligne suivi de texte : le bloc ne doit pas l'absorber
        return neuf

    return _IMG.sub(remplace, md)


_BLOC = re.compile(r"<div\b([^>]*\bdata-img-wysiwyg\b[^>]*)><figure>.*?</figure></div>", re.S)


def reconvertit_contenu(md):
    """Opération inverse (au mieux) : images de l'éditeur -> <content-img>."""

    def remplace(m):
        attrs = {}
        for a in _ATTR.finditer(m.group(1)):
            valeur = next((g for g in a.groups()[1:] if g is not None), "")
            attrs[a.group(1).lower()] = _html.unescape(valeur)
        src = attrs.get("data-img-wysiwyg", "")
        if not src or _ABSOLU.match(src):
            return m.group(0)  # adresse complète : content-img la préfixerait à tort
        morceaux = []
        align = attrs.get("data-align")
        if align == "center":
            morceaux.append("center")
        elif align in ("float-left", "float-right"):
            morceaux.append('float="%s"' % align.split("-")[1])
        elif align == "right":
            morceaux.append('float="right"')
        if "data-risetitre" in attrs:
            morceaux.append("risetitle")
        morceaux.append('src="%s"' % _attr(src))
        for donnee, nom in (("data-titre", "title"), ("data-source", "source"), ("data-lien", "link")):
            if attrs.get(donnee):
                morceaux.append('%s="%s"' % (nom, _attr(attrs[donnee])))
        if attrs.get("data-largeur"):
            morceaux.append('width="%s"' % attrs["data-largeur"])
        return "<content-img %s></content-img>" % " ".join(morceaux)

    return _BLOC.sub(remplace, md)


def _transforme(fonction, motif):
    connexion = op.get_bind()
    lignes = connexion.execute(
        sa.text("SELECT id_content, md FROM oeasc_commons.t_contents WHERE md LIKE :motif"),
        {"motif": motif},
    ).fetchall()
    for id_content, md in lignes:
        neuf = fonction(md)
        if neuf != md:
            connexion.execute(
                sa.text("UPDATE oeasc_commons.t_contents SET md = :md WHERE id_content = :id"),
                {"md": neuf, "id": id_content},
            )


def upgrade():
    _transforme(convertit_contenu, "%<content-img%")


def downgrade():
    _transforme(reconvertit_contenu, "%data-img-wysiwyg%")
