#####################################################################################
####### Recherches toutes les déclaration à renouveler et envoie un mail avec
####### un lien de renouvellement ou de clôture de la déclaration
####### Ce script est lancé par une tâche cron tous les mois
#####################################################################################
from flask import current_app, render_template, redirect
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from oeasc.modules.oeasc.declaration.repository import (
    get_user,
    liste_declarations_a_renouveler,
    check_token_renouvellement_declaration,
)
from oeasc.modules.oeasc.declaration.mail import generate_token
from oeasc.modules.oeasc.user.utils import check_auth_redirect_login
from oeasc.modules.oeasc.user.api import logout_external
from oeasc.modules.oeasc.declaration.mail import mail
from oeasc.modules.oeasc.declaration.models import TDeclaration
from sqlalchemy import update
import json



import click
import time
from flask.cli import with_appcontext
from flask_mail import Message
from datetime import datetime

@click.command('send-relance')
@with_appcontext
def send_relance_command():
    """Envoie les emails de relance aux déclarations concernées"""
    
    declarations = TDeclaration.query.filter_by(
        statut='relance'
    ).all()
    
    total = len(declarations)
    
    if total == 0:
        click.echo("Aucune déclaration à relancer")
        return
    
    click.echo(f"📧 {total} email(s) à envoyer...")
    
    for index, declaration in enumerate(declarations, 1):
        try:
            msg = Message(
                subject="Relance - Votre déclaration",
                recipients=[declaration.user.email],  # adapte selon ton modèle
                html=f"""
                    <h1>Bonjour {declaration.user.name}</h1>
                    <p>Votre déclaration du {declaration.created_at} nécessite votre attention.</p>
                """
            )
            mail.send(msg)
            
            # Optionnel : mettre à jour le statut après envoi
            declaration.statut = 'relance_envoyee'
            declaration.relance_sent_at = datetime.utcnow()
            db.session.commit()
            
            click.echo(f"✅ [{index}/{total}] Envoyé à {declaration.user.email}")
            
        except Exception as e:
            click.echo(f"❌ [{index}/{total}] Echec : {str(e)}")
        
        if index < total:
            time.sleep(1)
    
    click.echo(f"\n✅ Terminé : {total} emails traités")