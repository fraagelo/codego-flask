from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import get_db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def login():
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def login_post():
    usuario = request.form["usuario"]
    senha = request.form["senha"]

    with get_db() as db:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario=%s", (usuario,))
        user = cursor.fetchone()

    if user:
        session["username"] = user["usuario"]
        session["role"] = user["role"]
        return redirect(url_for("dashboard.dashboard"))

    return "Login inválido"

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
            token = serializer.dumps({'user_id': user_id}, salt='recover')

            # Gerar o link de redefinição
            reset_url = url_for('redefinir_senha', token=token, _external=True)

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
                return redirect(url_for('login'))

            except Exception as e:
                flash(f'Erro ao enviar e-mail: {str(e)}. Tente novamente mais tarde.', 'danger')
                return render_template('recuperar_senha.html')

        except Exception as e:
            flash(f'Erro ao processar a recuperação: {str(e)}', 'danger')
            return render_template('recuperar_senha.html')

    # Se for GET, só mostra o formulário
    return render_template('recuperar_senha.html')