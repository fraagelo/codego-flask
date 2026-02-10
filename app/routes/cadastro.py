from flask import Blueprint, render_template, request
from app.db import get_db

cadastro_bp = Blueprint("cadastro", __name__)

@cadastro_bp.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@cadastro_bp.route("/salvar_cadastro", methods=["POST"])
def salvar_cadastro():
    empresa = request.form["empresa"]

    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO empresas (empresa) VALUES (%s)",
            (empresa,)
        )
        db.commit()

    return "Salvo"
