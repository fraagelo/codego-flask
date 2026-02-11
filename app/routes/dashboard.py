from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route('/menu')
def menu():
    if session.get('role') not in ('assent','admin'): return redirect(url_for('auth.login'))
    return render_template('menu.html')

@dashboard_bp.route('/menu_jur')
def menu_jur():
    if session.get('role') != 'jur': return redirect(url_for('auth.login'))
    return render_template('menu_jur.html')