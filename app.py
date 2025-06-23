# app.py (organizado com seções comentadas)

from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)

# ==================== CONTEXT PROCESSOR ====================
@app.context_processor
def inject_now():
    return {'current_year': datetime.now().year}

# ==================== ROTAS BÁSICAS ====================

@app.route('/')
def index():
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    senha = request.form['senha']
    if usuario == 'admin' and senha == 'Novatecti':
        session['usuario'] = usuario
        return redirect(url_for('dashboard'))
    return 'Login inválido'

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

# ==================== ROTAS DE EMPRESA ====================

@app.route('/empresa/nova', methods=['GET', 'POST'])
def nova_empresa():
    if 'usuario' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome = request.form['nome']
        cnpj = request.form['cnpj']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO empresas (nome, cnpj) VALUES (%s, %s)", (nome, cnpj))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('listar_empresas'))

    return render_template('cadastrar_empresa.html')

@app.route('/empresas')
def listar_empresas():
    if 'usuario' not in session:
        return redirect(url_for('index'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM empresas")
    empresas = cursor.fetchall()
    cursor.close()
    return render_template('listar_empresas.html', empresas=empresas)

@app.route('/empresa/editar/<int:id>', methods=['GET', 'POST'])
def editar_empresa(id):
    if 'usuario' not in session:
        return redirect(url_for('index'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        nome = request.form['nome']
        cnpj = request.form['cnpj']
        cursor.execute("UPDATE empresas SET nome = %s, cnpj = %s WHERE id = %s", (nome, cnpj, id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('listar_empresas'))

    cursor.execute("SELECT * FROM empresas WHERE id = %s", (id,))
    empresa = cursor.fetchone()
    cursor.close()
    return render_template('editar_empresa.html', empresa=empresa)

@app.route('/empresa/excluir/<int:id>')
def excluir_empresa(id):
    if 'usuario' not in session:
        return redirect(url_for('index'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM empresas WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('listar_empresas'))

# ==================== ROTAS DE COMPUTADORES ====================

@app.route('/empresa/<int:empresa_id>/computador/novo', methods=['GET', 'POST'])
def cadastrar_computador(empresa_id):
    if 'usuario' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        dados = request.form
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO computadores 
            (empresa_id, nome_maquina, processador, memoria, armazenamento, espaco_livre, tipo_disco, anydesk_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            empresa_id,
            dados['nome_maquina'],
            dados['processador'],
            dados['memoria'],
            dados['armazenamento'],
            dados['espaco_livre'],
            dados['tipo_disco'],
            dados['anydesk_code']
        ))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('listar_computadores', empresa_id=empresa_id))

    return render_template('cadastrar_computador.html', empresa_id=empresa_id)

@app.route('/empresa/<int:empresa_id>/computadores')
def listar_computadores(empresa_id):
    if 'usuario' not in session:
        return redirect(url_for('index'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM computadores WHERE empresa_id = %s", (empresa_id,))
    computadores = cursor.fetchall()

    cursor.execute("SELECT nome FROM empresas WHERE id = %s", (empresa_id,))
    empresa = cursor.fetchone()

    cursor.close()
    return render_template(
        'listar_computadores.html',
        computadores=computadores,
        empresa_id=empresa_id,
        empresa_nome=empresa['nome'] if empresa else 'Empresa'
    )

@app.route('/computador/<int:id>/editar/<int:empresa_id>', methods=['GET', 'POST'])
def editar_computador(id, empresa_id):
    if 'usuario' not in session:
        return redirect(url_for('index'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        dados = request.form
        cursor.execute("""
            UPDATE computadores SET 
                nome_maquina=%s, processador=%s, memoria=%s, armazenamento=%s, espaco_livre=%s, tipo_disco=%s, anydesk_code=%s
            WHERE id=%s
        """, (
            dados['nome_maquina'], dados['processador'], dados['memoria'], dados['armazenamento'],
            dados['espaco_livre'], dados['tipo_disco'], dados['anydesk_code'], id
        ))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('listar_computadores', empresa_id=empresa_id))

    cursor.execute("SELECT * FROM computadores WHERE id = %s", (id,))
    computador = cursor.fetchone()
    cursor.close()

    return render_template('editar_computador.html', computador=computador, empresa_id=empresa_id)

@app.route('/computador/<int:id>/excluir/<int:empresa_id>')
def excluir_computador(id, empresa_id):
    if 'usuario' not in session:
        return redirect(url_for('index'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM computadores WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('listar_computadores', empresa_id=empresa_id))

@app.route('/computador/<int:id>/concluir/<int:empresa_id>')
def marcar_concluido(id, empresa_id):
    if 'usuario' not in session:
        return redirect(url_for('index'))

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE computadores SET concluido = 1 WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('listar_computadores', empresa_id=empresa_id))

@app.route('/computador/<int:id>/resetar/<int:empresa_id>')
def resetar_status(id, empresa_id):
    if 'usuario' not in session:
        return redirect(url_for('index'))

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE computadores SET concluido = 0 WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('listar_computadores', empresa_id=empresa_id))

# ==================== INICIAR APP ====================

if __name__ == '__main__':
    app.run(debug=True)