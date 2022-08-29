import click

from flask import Flask

from flask_bcrypt import (
    generate_password_hash
)

@app.cli.command()
@click.argument('password')
def password_hash(password):

    password_hash = generate_password_hash(password.encode('utf-8')).decode('utf-8')
