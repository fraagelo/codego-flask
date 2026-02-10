from flask import Blueprint, render_template

relatorio_bp = Blueprint("relatorio", __name__)

@relatorio_bp.route("/relatorios")
def relatorios():
    return render_template("relatorios.html")
