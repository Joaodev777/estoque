from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import random


app = Flask(__name__)

# Connect to the SQLite database (or create the database file if it doesn't exist)
conn = sqlite3.connect('estoque.db', check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()



cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        cod INTEGER PRIMARY KEY,
        nome TEXT,
        mac TEXT,
        modelo TEXT,
        custo TEXT,
        observacao TEXT,
        fornecedor TEXT,  -- Adicionando a coluna 'fornecedor'
        status TEXT DEFAULT 'ativo'
    )
''')



# Create the 'saidas' table if it doesn't exist
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS saidas (
#         id INTEGER PRIMARY KEY,
#         cod_produto INTEGER,
#         motivo_saida TEXT,
#         tecnico_response TEXT,
#         cliente_passado_materiais TEXT,
#         data_de_saida TEXT,
#         FOREIGN KEY (cod_produto) REFERENCES produtos (cod)
#     )
# ''')



# Altere a criação da tabela 'saidas', adicionando a coluna 'nome_produto'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS saidas (
        id INTEGER PRIMARY KEY,
        cod_produto INTEGER,
        nome_produto TEXT,
        motivo_saida TEXT,
        tecnico_response TEXT,
        cliente_passado_materiais TEXT,
        data_de_saida TEXT,
        observacao TEXT,
        fornecedor TEXT,  -- Adicionando a coluna 'fornecedor'
        FOREIGN KEY (cod_produto) REFERENCES produtos (cod)
    )
''')




cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos_apagados (
        cod INTEGER PRIMARY KEY,
        nome TEXT,
        mac TEXT,
        modelo TEXT,
        custo TEXT,
        observacao TEXT
    )
''')



conn.commit()



@app.route('/')
def index():
    # Consulta para obter todas as saídas
    cursor.execute("SELECT * FROM saidas")
    todas_saidas = cursor.fetchall()

    # Consulta para obter produtos ativos
    cursor.execute('SELECT * FROM produtos WHERE status = "ativo"')
    estoque = [{'cod': row[0], 'nome': row[1], 'mac': row[2], 'modelo': row[3], 'fornecedor': row[6], 'custo': row[4], 'observacao': row[5]} for row in cursor.fetchall()]

    return render_template('index.html', estoque=estoque, todas_saidas=todas_saidas)



@app.route('/filtrar_produtos', methods=['POST'])
def filtrar_produtos():
    filtro = request.form['filtro']
    termo = request.form['termo']

    if filtro == 'cod':
        cursor.execute('SELECT * FROM produtos WHERE cod = ?', (termo,))
    elif filtro == 'nome':
        cursor.execute('SELECT * FROM produtos WHERE nome LIKE ?', ('%' + termo + '%',))
    elif filtro == 'vac':
        return redirect(url_for('index'))
    elif filtro == 'modelo':
        cursor.execute('SELECT * FROM produtos WHERE modelo LIKE ?', ('%' + termo + '%',))
    elif filtro == '':
        cursor.execute('SELECT * FROM produtos WHERE modelo LIKE ?', ('%' + termo + '%',))
    elif filtro == 'custo':
        cursor.execute('SELECT * FROM produtos WHERE custo = ?', (termo,))
    elif filtro == 'mac':
        cursor.execute('SELECT * FROM produtos WHERE mac = ?', (termo,))
   

    estoque = [{'cod': row[0], 'nome': row[1], 'mac': row[2], 'modelo': row[3], 'custo': row[4]} for row in cursor.fetchall()]
    return render_template('index.html', estoque=estoque)



# @app.route('/excluir_produto', methods=['POST'])
# def excluir_produto():
#     try:
#         cod_produto = int(request.form['cod'])

#         cursor.execute('DELETE FROM produtos WHERE cod = ?', (cod_produto,))
#         conn.commit()
#     except Exception as e:
#         print(f"Error: {str(e)}")

#     return redirect(url_for('index'))


# @app.route('/cadastrar_produto', methods=['POST'])
# def cadastrar_produto():
#     nome = request.form['nome']
#     mac = request.form['mac']
#     modelo = request.form['modelo']
#     custo = float(request.form['custo'])
#     cod_produto = random.randint(10**2, 5**10 - 1)

#     cursor.execute('INSERT INTO produtos (cod, nome, mac, modelo, custo) VALUES (?, ?, ?, ?, ?)', (cod_produto, nome, mac, modelo, custo))
#     conn.commit()

#     return redirect(url_for('index'))



@app.route('/cadastrar_produto', methods=['POST'])
def cadastrar_produto():
    global max_cod

    # Aumente o contador máximo de código de produto
    max_cod = 00000 + 1

    # Use o valor atual do contador como código de produto
    cod_produto = max_cod

    nome = request.form['nome']
    mac = request.form['mac']
    modelo = request.form['modelo']
    custo = float(request.form['custo'])
    observacao = request.form['observacao']
    fornecedor = request.form['fornecedor']

    cursor.execute('INSERT INTO produtos (cod, nome, mac, modelo, custo, observacao, fornecedor) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (cod_produto, nome, mac, modelo, custo, observacao, fornecedor))
    conn.commit()

    return redirect(url_for('index'))


# ...

# Atualize a função 'baixar_produto' para incluir o fornecedor e decorá-la como rota
@app.route('/baixar_produto', methods=['POST'])
def baixar_produto():
    try:
        cod_produto = int(request.form['cod_produto'])
        motivo_saida = request.form['motivo_saida']
        tecnico_response = request.form['tecnico_response']
        cliente_passado_materiais = request.form['cliente_passado_materiais']
        observacao = request.form['observacao']
        fornecedor = request.form['fornecedor']  # Obtenha o fornecedor do formulário

        # Obtenha a data atual no formato YYYY-MM-DD
        data_de_saida = datetime.now().strftime('%d-%m-%Y')

        # Obtenha os dados do produto antes de excluir
        cursor.execute('SELECT * FROM produtos WHERE cod = ?', (cod_produto,))
        produto = cursor.fetchone()

        # Inserir dados na tabela de saidas, incluindo o nome do produto e fornecedor
        cursor.execute('''
            INSERT INTO saidas (cod_produto, nome_produto, motivo_saida, tecnico_response, cliente_passado_materiais, data_de_saida, observacao, fornecedor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cod_produto, produto['nome'], motivo_saida, tecnico_response, cliente_passado_materiais, data_de_saida, observacao, fornecedor))

        # Excluir o produto da tabela 'produtos'
        cursor.execute('DELETE FROM produtos WHERE cod = ?', (cod_produto,))
        conn.commit()

        # Filtrar produtos e mostrar a lista
        return redirect(url_for('index'))

    except Exception as e:
        print(f"Error: {str(e)}")

    return redirect(url_for('index'))

# ...




@app.errorhandler(404)
def page_not_found(e):
    return "404 - Page not found", 404

if __name__ == '__main__':
    app.run(debug=True)
