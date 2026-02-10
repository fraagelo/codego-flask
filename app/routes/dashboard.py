from flask import Blueprint, render_template, session

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    if "username" not in session:
        return "Não autorizado"

    return render_template("dashboard.html")
