import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'chave_secreta_super_segura' # Em produção, use uma chave aleatória

# --- CONFIGURAÇÃO DE UPLOAD ---
# Define onde as imagens serão salvas
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- BANCO DE DADOS ---
def get_db_connection():
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- ROTAS PÚBLICAS ---

@app.route('/')
def home():
    # Na Home, vamos mostrar os itens em destaque (opcional: últimos 3 de cada)
    conn = get_db_connection()
    noticias = conn.execute('SELECT * FROM postagens ORDER BY data_criacao DESC LIMIT 3').fetchall()
    locais = conn.execute('SELECT * FROM diretorio ORDER BY random() LIMIT 4').fetchall()
    conn.close()
    return render_template('index.html', noticias=noticias, locais=locais)

@app.route('/feed')
def feed():
    conn = get_db_connection()
    # Busca postagens unindo com a tabela de usuários para saber quem postou (autor)
    sql = '''
        SELECT postagens.*, usuarios.nome as autor_nome, usuarios.foto_perfil 
        FROM postagens 
        JOIN usuarios ON postagens.usuario_id = usuarios.id 
        ORDER BY data_criacao DESC
    '''
    postagens = conn.execute(sql).fetchall()
    conn.close()
    return render_template('feed.html', postagens=postagens)

@app.route('/diretorio')
def diretorio():
    conn = get_db_connection()
    # Filtros simples via URL (ex: /diretorio?categoria=Saúde)
    categoria_filtro = request.args.get('categoria')
    
    if categoria_filtro:
        itens = conn.execute('SELECT * FROM diretorio WHERE categoria = ? ORDER BY nome', (categoria_filtro,)).fetchall()
    else:
        itens = conn.execute('SELECT * FROM diretorio ORDER BY nome').fetchall()
    
    conn.close()
    return render_template('diretorio.html', itens=itens)

@app.route('/detalhes/<int:id>')
def detalhes_local(id):
    conn = get_db_connection()
    # Busca o item específico pelo ID
    item = conn.execute('SELECT * FROM diretorio WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if item is None:
        return "Local não encontrado", 404
        
    return render_template('detalhes.html', item=item)
    
@app.route('/marketplace')
def marketplace():
    conn = get_db_connection()
    
    # Pega os filtros da URL (ex: ?tipo=oferta ou ?q=carro)
    tipo_filtro = request.args.get('tipo') # pode ser 'oferta' ou 'procura'
    busca = request.args.get('q')          # O que a pessoa digitou na pesquisa

    # Começa a montar o SQL
    # Fazemos JOIN com usuarios para mostrar o nome/foto de quem anunciou
    sql = '''
        SELECT marketplace.*, usuarios.nome as autor_nome, usuarios.foto_perfil 
        FROM marketplace 
        JOIN usuarios ON marketplace.usuario_id = usuarios.id 
        WHERE 1=1
    '''
    params = []

    # Se clicou num filtro (Oferta ou Procura), adiciona ao SQL
    if tipo_filtro:
        sql += " AND tipo_anuncio = ?"
        params.append(tipo_filtro)
    
    # Se digitou algo na busca, pesquisa no Título, Descrição ou Categoria
    if busca:
        sql += " AND (titulo LIKE ? OR descricao LIKE ? OR categoria LIKE ?)"
        termo = f'%{busca}%' # O % serve para buscar "carro" dentro de "carroceria"
        params.extend([termo, termo, termo])

    sql += " ORDER BY data_criacao DESC"
    
    anuncios = conn.execute(sql, params).fetchall()
    conn.close()
    
    return render_template('marketplace.html', anuncios=anuncios, tipo_ativo=tipo_filtro)

@app.route('/anunciar', methods=['GET', 'POST'])
def anunciar():
    # 1. Verifica se o usuário está logado (só cidadãos logados podem anunciar)
    if 'user_id' not in session:
        flash('Você precisa fazer login ou se registrar para criar um anúncio.')
        return redirect(url_for('login'))

    # 2. Se o formulário foi enviado (POST)
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        tipo_anuncio = request.form['tipo_anuncio'] # 'oferta' ou 'procura'
        categoria = request.form['categoria']
        preco = request.form.get('preco', '') # Opcional
        contato = request.form['contato']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO marketplace (titulo, descricao, tipo_anuncio, categoria, preco, contato, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (titulo, descricao, tipo_anuncio, categoria, preco, contato, session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Seu anúncio foi publicado com sucesso!')
        return redirect(url_for('marketplace'))

    # 3. Se for apenas para abrir a página (GET)
    # Sugere o contato que o usuário usou no cadastro (telefone ou email)
    contato_padrao = session.get('user_contato', '')
    
    return render_template('anunciar.html', contato_padrao=contato_padrao)
    
# --- AUTENTICAÇÃO (LOGIN / REGISTRO) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # O campo agora se chama 'login_input' (pode ser email ou telefone)
        login_input = request.form['login_input']
        senha = request.form['senha']
        
        conn = get_db_connection()
        # A mágica do SQL: procura se o texto digitado bate com email OU telefone
        user = conn.execute('SELECT * FROM usuarios WHERE email = ? OR telefone = ?', 
                            (login_input, login_input)).fetchone()
        conn.close()
        
        if user and user['senha'] == senha:
            session['user_id'] = user['id']
            session['user_nome'] = user['nome']
            # Salva o contato que existir (email ou telefone)
            session['user_contato'] = user['email'] if user['email'] else user['telefone']
            session['user_funcao'] = user['funcao']
            
            flash(f'Bem-vindo de volta, {user["nome"]}!')
            
            if user['funcao'] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Dados de acesso incorretos.')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        bio = request.form['bio']
        
        # Pega os dados (podem vir vazios)
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        
        # Validação: Tem que ter pelo menos um dos dois!
        if not email and not telefone:
            flash('Erro: Você precisa fornecer um E-mail ou um Telefone.')
            return render_template('register.html')

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO usuarios (nome, email, telefone, senha, bio, funcao) VALUES (?, ?, ?, ?, ?, ?)',
                         (nome, email, telefone, senha, bio, 'cidadao'))
            conn.commit()
            flash('Cadastro realizado! Faça login para continuar.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Erro: Este e-mail ou telefone já está cadastrado.')
        finally:
            conn.close()
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.')
    return redirect(url_for('login'))

# --- ÁREA ADMINISTRATIVA ---

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Verifica se está logado E se é admin
    if 'user_id' not in session or session.get('user_funcao') != 'admin':
        flash('Acesso negado. Apenas administradores.')
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        acao = request.form.get('acao')

        # 1. Nova Postagem
        if acao == 'nova_postagem':
            titulo = request.form['titulo']
            conteudo = request.form['conteudo']
            categoria = request.form['categoria']
            
            conn.execute('INSERT INTO postagens (titulo, conteudo, categoria, usuario_id) VALUES (?, ?, ?, ?)',
                         (titulo, conteudo, categoria, session['user_id']))
            conn.commit()
            flash('Postagem publicada!')

        # 2. Novo Local no Diretório (Atualizado com novos campos)
        # 2. Novo Local no Diretório (COM UPLOAD DE IMAGEM)
        elif acao == 'novo_item_diretorio':
            nome = request.form['nome']
            categoria = request.form['categoria']
            subcategoria = request.form['subcategoria']
            tipo = request.form['tipo']
            telefone = request.form['telefone']
            endereco = request.form['endereco']
            horario = request.form['horario']
            descricao = request.form['descricao']
            historia = request.form['historia']
            
            # Lógica de Imagem
            arquivo = request.files.get('imagem') # Pega o arquivo do form
            nome_imagem = 'default_cover.jpg'     # Se não enviar nada, usa a padrão

            if arquivo and arquivo.filename != '':
                # Cria um nome seguro (ex: 'Minha Foto.jpg' vira 'Minha_Foto.jpg')
                nome_seguro = secure_filename(arquivo.filename)
                
                # Adiciona um número aleatório no inicio para não substituir fotos com mesmo nome
                import random
                prefixo = str(random.randint(1000, 9999))
                nome_final = f"{prefixo}_{nome_seguro}"
                
                # Salva na pasta correta
                caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], 'capas', nome_final)
                arquivo.save(caminho_salvar)
                
                nome_imagem = nome_final # Atualiza o nome para salvar no banco

            # Salva no Banco de Dados
            conn.execute('''
                INSERT INTO diretorio 
                (nome, categoria, subcategoria, tipo, telefone, endereco, horario, descricao_curta, historia_completa, imagem_capa, autor_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome, categoria, subcategoria, tipo, telefone, endereco, horario, descricao, historia, nome_imagem, session['user_id']))
            
            conn.commit()
            flash('Local adicionado com foto!')

    # Dados para exibição
    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()
    postagens = conn.execute('SELECT * FROM postagens ORDER BY data_criacao DESC').fetchall()
    diretorio = conn.execute('SELECT * FROM diretorio ORDER BY nome').fetchall()
    conn.close()

    return render_template('admin.html', usuario=session['user_nome'], usuarios=usuarios, postagens=postagens, itens_diretorio=diretorio)

if __name__ == '__main__':
    app.run(debug=True)