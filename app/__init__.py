from flask import Flask, session, redirect, url_for, request
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    @app.before_request
    def verificar_login():

        rotas_publicas = (
            'auth.login',
            'auth.recuperar_senha',
            'auth.redefinir_senha',
            'auth.registrar_usuario',
            'static'
        )

        if request.endpoint is None:
            return

        if request.endpoint.startswith('static'):
            return

        if request.endpoint in rotas_publicas:
            return

        if 'username' not in session:
            return redirect(url_for('auth.login'))



    # registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.cadastro import cadastro_bp
    from app.routes.relatorios import relatorio_bp
    from app.routes.logs import logs_bp
    from app.routes.edicao import edicao_bp
    from app.routes.juridico import juridico_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(cadastro_bp)
    app.register_blueprint(relatorio_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(edicao_bp)
    app.register_blueprint(juridico_bp)

    return app
