from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.db import get_db
from itsdangerous import URLSafeTimedSerializer
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

auth_bp = Blueprint("auth", __name__)

def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

@auth_bp.route("/")
def index():
    return render_template("login.html")

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            with get_db() as db:
                with db.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM usuarios WHERE login = %s", (username,))
                    usuario = cursor.fetchone()
                    if usuario and bcrypt.check_password_hash(usuario['senha'], password):
                        session['username'] = usuario['login']
                        if usuario['departamento'] == 'Jurídico':
                            session['role'] = 'jur'
                            return redirect(url_for('dashboard.menu_jur'))
                        elif usuario['departamento'] == 'Assentamento':
                            session['role'] = 'assent'
                            return redirect(url_for('dashboard.menu'))
                        elif usuario['departamento'] == 'admin':
                            session['role'] = 'admin'
                            return redirect(url_for('dashboard.menu'))
                    else:
                        flash('Usuário ou senha inválidos!', 'danger')
        except Exception as e:
            flash(f'Erro ao fazer login: {e}', 'danger')

    return render_template('login.html')

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        if not email:
            flash('Por favor, informe seu e-mail cadastrado.', 'danger')
            return render_template('recuperar_senha.html')
        
        try:
            # Buscar usuário pelo login
            with get_db() as db:
                cursor = db.cursor(dictionary=True)
                cursor.execute("SELECT id, login, email FROM usuarios WHERE email = %s", (email,))
                user = cursor.fetchone()
                cursor.close()

            if not user:
                # Mesmo se não existir, mostra a mesma mensagem para segurança
                flash('Se o e-mail for válido, enviaremos instruções de recuperação.', 'info')
                return render_template('recuperar_senha.html')
            
            user_id = user['id']
            login_usuario = user['login']
            email_usuario = user['email']

            # Gerar um token com expiração de 15 minutos
            serializer = get_serializer()
            token = serializer.dumps({'user_id': user_id}, salt='recover')

            # Gerar o link de redefinição
            reset_url = url_for('auth.redefinir_senha', token=token, _external=True)

            # Montar o e-mail (copie sua estrutura de e-mail já usada no seu sistema)
            subject = "Recuperação de senha - CODEGO"
            body = f"""
Olá {login_usuario},

Você solicitou a recuperação de sua senha no sistema CODEGO.

Para redefinir sua senha, clique no link abaixo:

{reset_url}

Este link é válido por 15 minutos apenas.

Se você não solicitou, ignore este e-mail.

Atenciosamente,
Equipe CODEGO
"""
            # Enviar o e‑mail via gmail
            try:
                # Configuração do gmail
                smtp_server = 'smtp.gmail.com'
                smtp_port = 587
                smtp_username = 'emailsendercodego@gmail.com'
                smtp_password = 'sxlf wwsk woha cxuc'

                msg = MIMEMultipart()
                msg['From'] = smtp_username
                msg['To'] = email_usuario
                msg['Subject'] = subject

                msg.attach(MIMEText(body, 'plain', 'utf-8'))

                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(smtp_username, [email_usuario], msg.as_string())
                server.quit()

                flash('Se o e-mail for válido, enviaremos instruções de recuperação para o e-mail cadastrado.', 'info')
                return redirect(url_for('auth.login'))

            except Exception as e:
                flash(f'Erro ao enviar e-mail: {str(e)}. Tente novamente mais tarde.', 'danger')
                return render_template('recuperar_senha.html')

        except Exception as e:
            flash(f'Erro ao processar a recuperação: {str(e)}', 'danger')
            return render_template('recuperar_senha.html')

    # Se for GET, só mostra o formulário
    return render_template('recuperar_senha.html')

@auth_bp.route('/registrar-usuario', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        nome = request.form.get('nome')
        login = request.form.get('login')
        email = request.form.get('email')
        senha = request.form.get('senha')
        departamento = request.form.get('departamento', '')

        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

        # Validação básica
        if not nome or not login or not email or not senha:
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'danger')
            return render_template('registrar_usuario.html')

        try:
            with get_db() as db:
                with db.cursor() as cursor:
                    # Supondo que você tenha uma tabela 'usuarios' com os campos abaixo
                    cursor.execute("""
                        INSERT INTO usuarios (nome, login, email, senha, departamento)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (nome, login, email, senha_hash, departamento))
                    db.commit()
                flash('Usuário registrado com sucesso!', 'success')
                return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Erro ao registrar usuário: {e}', 'danger')

    return render_template('registrar_usuario.html')

@auth_bp.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    try:
        serializer = get_serializer()
        data = serializer.loads(token, salt='recover', max_age=900)
        user_id = data['user_id']
    except Exception as e:
        flash('Link inválido ou expirado.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        senha = request.form.get('senha', '').strip()
        confirmar = request.form.get('confirmar', '').strip()
        
        if not senha or senha != confirmar:
            flash('As senhas não conferem ou estão vazias.', 'danger')
            return render_template('redefinir_senha.html', token=token)

        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')
        
        try:
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute("UPDATE usuarios SET senha = %s WHERE id = %s", (senha_hash, user_id))
                db.commit()
                cursor.close()
                db.close()
                flash('Senha alterada com sucesso!', 'success')
                return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Erro ao salvar senha: {str(e)}', 'danger')
            return render_template('redefinir_senha.html', token=token)
    
    return render_template('redefinir_senha.html', token=token)