from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.db import get_db
from app.services.log_service import gravar_log

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

@cadastro_bp.route('/cadastro_jur', methods=['GET', 'POST'])
def cadastro_jur():
    if session.get('role') != 'jur': return redirect(url_for('login'))
    
    if request.method == 'POST':
        empresa_id = request.form.get('empresa_id')
        dados_jur = {
            'processo_judicial': request.form.get('processo_judicial', ''),
            'status': request.form.get('status', ''),
            'assunto_judicial': request.form.get('assunto_judicial', ''),
            'valor_da_causa': request.form.get('valor_da_causa', '')
        }
        
        try:
            with get_db() as db:
                with db.cursor() as cursor:
                    set_clause = ", ".join([f"`{k}` = %s" for k in dados_jur.keys()])
                    query = f"UPDATE municipal_lots SET {set_clause} WHERE id = %s"
                    cursor.execute(query, list(dados_jur.values()) + [empresa_id])
                    db.commit()
                    gravar_log(f"CADASTRO_JURIDICO_INICIAL (ID {empresa_id})", db_conn=db)
            flash('Informações jurídicas adicionadas com sucesso!', 'success')
            return redirect(url_for('menu_jur'))
        except Exception as e:
            flash(f'Erro ao salvar: {e}', 'danger')

    # Lógica GET: Busca empresas que não possuem dados jurídicos preenchidos
    empresas_pendentes = []
    try:
        with get_db() as db:
            with db.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT id, empresa, cnpj FROM municipal_lots 
                    WHERE (processo_judicial IS NULL OR processo_judicial = '' OR processo_judicial = '-')
                    AND empresa != '-' ORDER BY empresa
                """)
                empresas_pendentes = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao buscar empresas: {e}")

    return render_template('cadastro_jur.html', empresas=empresas_pendentes, username=session.get('username'))
