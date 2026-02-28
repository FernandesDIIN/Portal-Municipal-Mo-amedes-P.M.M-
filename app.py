import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
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

@app.route('/criar_postagem', methods=['GET', 'POST'])
def criar_postagem():
    if 'user_id' not in session:
        flash('Você precisa fazer login para publicar no Feed da Comunidade.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        conteudo = request.form['conteudo']
        categoria = request.form['categoria']
        
        # --- LÓGICA DE UPLOAD DE FOTOS ---
        imagem1 = request.files.get('imagem1')
        imagem2 = request.files.get('imagem2')
        
        nome_img1 = None
        nome_img2 = None
        import random
        
        # Cria a pasta para as fotos do feed se não existir
        pasta_feed = os.path.join(app.config['UPLOAD_FOLDER'], 'feed_imagens')
        os.makedirs(pasta_feed, exist_ok=True)

        if imagem1 and imagem1.filename != '':
            nome_seguro = secure_filename(imagem1.filename)
            nome_img1 = f"feed_1_{random.randint(1000, 9999)}_{nome_seguro}"
            imagem1.save(os.path.join(pasta_feed, nome_img1))

        if imagem2 and imagem2.filename != '':
            nome_seguro = secure_filename(imagem2.filename)
            nome_img2 = f"feed_2_{random.randint(1000, 9999)}_{nome_seguro}"
            imagem2.save(os.path.join(pasta_feed, nome_img2))
        
        # Guarda no banco
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO postagens (titulo, conteudo, categoria, usuario_id, imagem1, imagem2)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (titulo, conteudo, categoria, session['user_id'], nome_img1, nome_img2))
        conn.commit()
        conn.close()
        
        flash('Publicação enviada com sucesso para o Feed!')
        return redirect(url_for('feed'))

    return render_template('criar_postagem.html')
    
@app.route('/feed')
def feed():
    conn = get_db_connection()
    busca = request.args.get('q')
    
    # A MÁGICA DO ALGORITMO DE RELEVÂNCIA TEMPORAL (Estilo Reddit)
    sql = '''
        SELECT postagens.*, usuarios.nome as autor_nome, usuarios.foto_perfil,
        
        (upvotes / (((strftime('%s', 'now') - strftime('%s', data_criacao)) / 3600.0) + 2.0)) AS score_relevancia
        
        FROM postagens 
        JOIN usuarios ON postagens.usuario_id = usuarios.id 
        WHERE 1=1
    '''
    params = []

    if busca:
        sql += ' AND (titulo LIKE ? OR conteudo LIKE ? OR categoria LIKE ?)'
        termo = f'%{busca}%'
        params.extend([termo, termo, termo])
        
    # Ordenação Final: 
    # 1º Fixados (1 vem antes de 0)
    # 2º Score de Relevância calculado (Os mais quentes do momento)
    # 3º Data de Criação (Desempate para posts sem votos)
    sql += ' ORDER BY fixado DESC, score_relevancia DESC, data_criacao DESC'
    
    postagens = conn.execute(sql, params).fetchall()
    
    # Descobre em quais posts o usuário logado já votou
    meus_votos = []
    if 'user_id' in session:
        votos = conn.execute('SELECT postagem_id FROM postagens_upvotes WHERE usuario_id = ?', (session['user_id'],)).fetchall()
        meus_votos = [v['postagem_id'] for v in votos]
        
    conn.close()
    return render_template('feed.html', postagens=postagens, meus_votos=meus_votos)

@app.route('/diretorio')
def diretorio():
    conn = get_db_connection()
    
    categoria_filtro = request.args.get('categoria')
    busca = request.args.get('q') 
    
    # A MÁGICA: O SQL agora calcula a média (AVG) e o total (COUNT) de avaliações para cada local
    sql = '''
        SELECT diretorio.*, 
               AVG(avaliacoes.nota) as media_estrelas,
               COUNT(avaliacoes.id) as total_avaliacoes
        FROM diretorio 
        LEFT JOIN avaliacoes ON diretorio.id = avaliacoes.diretorio_id
        WHERE 1=1
    '''
    params = []

    if categoria_filtro:
        sql += ' AND diretorio.categoria = ?'
        params.append(categoria_filtro)
        
    if busca:
        sql += ' AND (diretorio.nome LIKE ? OR diretorio.descricao_curta LIKE ? OR diretorio.subcategoria LIKE ?)'
        termo = f'%{busca}%'
        params.extend([termo, termo, termo])
        
    sql += ' GROUP BY diretorio.id ORDER BY diretorio.nome'
    
    itens = conn.execute(sql, params).fetchall()
    conn.close()
    
    return render_template('diretorio.html', itens=itens)

@app.route('/detalhes/<int:id>')
def detalhes_local(id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM diretorio WHERE id = ?', (id,)).fetchone()
    fotos_galeria = conn.execute('SELECT * FROM galeria_diretorio WHERE diretorio_id = ?', (id,)).fetchall()
    
    # Busca todas as avaliações deste local
    avaliacoes = conn.execute('''
        SELECT avaliacoes.*, usuarios.nome as autor_nome 
        FROM avaliacoes 
        JOIN usuarios ON avaliacoes.usuario_id = usuarios.id 
        WHERE diretorio_id = ? 
        ORDER BY data_criacao DESC
    ''', (id,)).fetchall()
    
    # Calcula a nota média
    media_calc = conn.execute('SELECT AVG(nota) as media FROM avaliacoes WHERE diretorio_id = ?', (id,)).fetchone()['media']
    media_estrelas = round(media_calc, 1) if media_calc else 0
    total_avaliacoes = len(avaliacoes)
    
    # Verifica se o usuário atual já avaliou (para esconder o formulário e evitar spam)
    ja_avaliou = False
    if 'user_id' in session:
        voto_existente = conn.execute('SELECT id FROM avaliacoes WHERE diretorio_id = ? AND usuario_id = ?', (id, session['user_id'])).fetchone()
        if voto_existente:
            ja_avaliou = True
            
    conn.close()
    
    if item is None:
        return "Local não encontrado", 404
        
    return render_template('detalhes.html', item=item, fotos=fotos_galeria, avaliacoes=avaliacoes, media=media_estrelas, total=total_avaliacoes, ja_avaliou=ja_avaliou)

@app.route('/avaliar_local/<int:id>', methods=['POST'])
def avaliar_local(id):
    if 'user_id' not in session:
        flash('Você precisa fazer login para avaliar os locais.')
        return redirect(url_for('login'))
        
    nota = request.form.get('nota')
    comentario = request.form.get('comentario')
    
    if not nota:
        flash('Por favor, selecione uma nota de 1 a 5 estrelas.')
        return redirect(url_for('detalhes_local', id=id))
        
    conn = get_db_connection()
    conn.execute('INSERT INTO avaliacoes (diretorio_id, usuario_id, nota, comentario) VALUES (?, ?, ?, ?)',
                 (id, session['user_id'], int(nota), comentario))
    conn.commit()
    conn.close()
    
    flash('Avaliação publicada com sucesso! Obrigado por contribuir.')
    return redirect(url_for('detalhes_local', id=id))

@app.route('/upload_galeria/<int:id>', methods=['POST'])
def upload_galeria(id):
    if session.get('user_funcao') != 'admin':
        return "Acesso negado", 403

    titulo = request.form.get('titulo', '') # NOVO: Pega o título opcional
    arquivo = request.files.get('imagem_galeria')
    
    if arquivo and arquivo.filename != '':
        nome_seguro = secure_filename(arquivo.filename)
        import random
        nome_final = f"galeria_{id}_{random.randint(1000, 9999)}_{nome_seguro}"
        
        pasta_galeria = os.path.join(app.config['UPLOAD_FOLDER'], 'galeria')
        os.makedirs(pasta_galeria, exist_ok=True)
        
        arquivo.save(os.path.join(pasta_galeria, nome_final))
        
        conn = get_db_connection()
        # NOVO: Salva o título junto com o nome da imagem
        conn.execute('INSERT INTO galeria_diretorio (diretorio_id, nome_imagem, titulo) VALUES (?, ?, ?)', (id, nome_final, titulo))
        conn.commit()
        conn.close()
        
        flash('Foto adicionada à galeria com sucesso!')
        
    return redirect(url_for('detalhes_local', id=id))

@app.route('/deletar_foto_diretorio/<int:id>', methods=['POST'])
def deletar_foto_diretorio(id):
    if session.get('user_funcao') not in ['admin', 'mod']:
        flash('Acesso negado. Apenas administradores e moderadores podem apagar fotos do diretório.')
        return redirect(request.referrer or url_for('diretorio'))

    conn = get_db_connection()
    foto = conn.execute('SELECT * FROM galeria_diretorio WHERE id = ?', (id,)).fetchone()
    
    if foto:
        import os
        try:
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], 'galeria', foto['nome_imagem'])
            if os.path.exists(caminho):
                os.remove(caminho)
        except: 
            pass
            
        conn.execute('DELETE FROM galeria_diretorio WHERE id = ?', (id,))
        conn.commit()
        flash('Foto removida da galeria do local.')
        
    conn.close()
    return redirect(request.referrer)
    
@app.route('/marketplace')
def marketplace():
    conn = get_db_connection()
    
    tipo_filtro = request.args.get('tipo') 
    busca = request.args.get('q')          

    sql = '''
        SELECT marketplace.*, usuarios.nome as autor_nome, usuarios.foto_perfil 
        FROM marketplace 
        JOIN usuarios ON marketplace.usuario_id = usuarios.id 
        WHERE 1=1
    '''
    params = []

    if tipo_filtro:
        sql += " AND tipo_anuncio = ?"
        params.append(tipo_filtro)
    
    if busca:
        sql += " AND (titulo LIKE ? OR descricao LIKE ? OR categoria LIKE ?)"
        termo = f'%{busca}%' 
        params.extend([termo, termo, termo])

    sql += " ORDER BY data_criacao DESC"
    
    anuncios = conn.execute(sql, params).fetchall()
    conn.close()
    
    return render_template('marketplace.html', anuncios=anuncios, tipo_ativo=tipo_filtro)

@app.route('/anunciar', methods=['GET', 'POST'])
def anunciar():
    if 'user_id' not in session:
        flash('Você precisa fazer login ou se registrar para criar um anúncio.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        tipo_anuncio = request.form['tipo_anuncio']
        categoria = request.form['categoria']
        preco = request.form.get('preco', '') 
        contato = request.form['contato']
        
        # --- LÓGICA DE UPLOAD DAS DUAS IMAGENS ---
        imagem1 = request.files.get('imagem1')
        imagem2 = request.files.get('imagem2')
        
        nome_img1 = None
        nome_img2 = None
        import random
        
        pasta_mkt = os.path.join(app.config['UPLOAD_FOLDER'], 'marketplace')
        os.makedirs(pasta_mkt, exist_ok=True)

        if imagem1 and imagem1.filename != '':
            nome_seguro = secure_filename(imagem1.filename)
            nome_img1 = f"mkt_1_{random.randint(1000, 9999)}_{nome_seguro}"
            imagem1.save(os.path.join(pasta_mkt, nome_img1))

        if imagem2 and imagem2.filename != '':
            nome_seguro = secure_filename(imagem2.filename)
            nome_img2 = f"mkt_2_{random.randint(1000, 9999)}_{nome_seguro}"
            imagem2.save(os.path.join(pasta_mkt, nome_img2))
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO marketplace (titulo, descricao, tipo_anuncio, categoria, preco, contato, usuario_id, imagem1, imagem2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (titulo, descricao, tipo_anuncio, categoria, preco, contato, session['user_id'], nome_img1, nome_img2))
        conn.commit()
        conn.close()
        
        flash('Seu anúncio foi publicado com sucesso!')
        return redirect(url_for('marketplace'))

    contato_padrao = session.get('user_contato', '')
    return render_template('anunciar.html', contato_padrao=contato_padrao)
    
# --- AUTENTICAÇÃO (LOGIN / REGISTRO) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form['login_input']
        senha = request.form['senha']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE email = ? OR telefone = ?', 
                            (login_input, login_input)).fetchone()
        conn.close()
        
        if user and user['senha'] == senha:
            session['user_id'] = user['id']
            session['user_nome'] = user['nome']
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
        
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        
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
    if 'user_id' not in session or session.get('user_funcao') not in ['admin', 'mod']:
        flash('Acesso negado. Área restrita.')
        return redirect(url_for('login'))
        
    conn = get_db_connection()

    if request.method == 'POST':
        acao = request.form.get('acao')
        
        if acao == 'nova_postagem':
            titulo = request.form['titulo']
            conteudo = request.form['conteudo']
            categoria = request.form['categoria']
            
            conn.execute('INSERT INTO postagens (titulo, conteudo, categoria, usuario_id) VALUES (?, ?, ?, ?)',
                         (titulo, conteudo, categoria, session['user_id']))
            conn.commit()
            flash('Postagem publicada!')

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
            
            arquivo = request.files.get('imagem')
            nome_imagem = 'default_cover.jpg'

            if arquivo and arquivo.filename != '':
                nome_seguro = secure_filename(arquivo.filename)
                import random
                prefixo = str(random.randint(1000, 9999))
                nome_final = f"{prefixo}_{nome_seguro}"
                
                caminho_salvar = os.path.join(app.config['UPLOAD_FOLDER'], 'capas', nome_final)
                arquivo.save(caminho_salvar)
                
                nome_imagem = nome_final

            conn.execute('''
                INSERT INTO diretorio 
                (nome, categoria, subcategoria, tipo, telefone, endereco, horario, descricao_curta, historia_completa, imagem_capa, autor_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome, categoria, subcategoria, tipo, telefone, endereco, horario, descricao, historia, nome_imagem, session['user_id']))
            
            conn.commit()
            flash('Local adicionado com foto!')

    busca_user = request.args.get('q_user', '').strip()
    if busca_user:
        sql_users = 'SELECT * FROM usuarios WHERE email LIKE ? OR telefone LIKE ? OR nome LIKE ? OR CAST(id AS TEXT) = ? ORDER BY nome'
        termo_user = f'%{busca_user}%'
        params_users = [termo_user, termo_user, termo_user, busca_user]
    else:
        sql_users = 'SELECT * FROM usuarios ORDER BY id DESC LIMIT 3'
        params_users = []
        
    usuarios = conn.execute(sql_users, params_users).fetchall()

    busca_dir = request.args.get('q_dir', '').strip()
    if busca_dir:
        sql_dir = 'SELECT * FROM diretorio WHERE nome LIKE ? ORDER BY nome'
        termo_dir = f'%{busca_dir}%'
        params_dir = [termo_dir]
    else:
        sql_dir = 'SELECT * FROM diretorio ORDER BY id DESC LIMIT 2'
        params_dir = []
        
    diretorio = conn.execute(sql_dir, params_dir).fetchall()

    postagens = conn.execute('SELECT * FROM postagens ORDER BY data_criacao DESC').fetchall()
    
    conn.close()
    
    return render_template('admin.html', usuario=session.get('user_nome', ''), usuarios=usuarios, postagens=postagens, itens_diretorio=diretorio, itens=diretorio)

@app.route('/admin/deletar_usuario/<int:id>', methods=['POST'])
def deletar_usuario(id):
    if session.get('user_funcao') != 'admin':
        return "Acesso negado", 403
        
    if id == session['user_id']:
        flash('Você não pode excluir sua própria conta de Administrador!')
        return redirect(url_for('admin'))

    conn = get_db_connection()
    conn.execute('DELETE FROM postagens WHERE usuario_id = ?', (id,))
    conn.execute('DELETE FROM marketplace WHERE usuario_id = ?', (id,))
    conn.execute('DELETE FROM usuarios WHERE id = ?', (id,))
    
    conn.commit()
    conn.close()
    
    flash('Usuário e seus dados excluídos com sucesso!')
    return redirect(url_for('admin'))

@app.route('/galeria', methods=['GET', 'POST'])
def galeria():
    conn = get_db_connection()
    
    if request.method == 'POST' and session.get('user_funcao') == 'admin':
        titulo = request.form['titulo']
        local = request.form['local']
        arquivo = request.files.get('imagem')
        
        if arquivo and arquivo.filename != '':
            nome_seguro = secure_filename(arquivo.filename)
            import random
            nome_final = f"mun_{random.randint(1000, 9999)}_{nome_seguro}"
            
            pasta = os.path.join(app.config['UPLOAD_FOLDER'], 'galeria_municipio')
            os.makedirs(pasta, exist_ok=True)
            
            arquivo.save(os.path.join(pasta, nome_final))
            
            conn.execute('INSERT INTO galeria_municipio (titulo, local, nome_imagem) VALUES (?, ?, ?)', 
                         (titulo, local, nome_final))
            conn.commit()
            flash('Foto adicionada à galeria oficial!')
            return redirect(url_for('galeria'))

    fotos = conn.execute('SELECT * FROM galeria_municipio ORDER BY data_criacao DESC').fetchall()
    conn.close()
    
    return render_template('galeria.html', fotos=fotos)

@app.route('/deletar_foto_galeria/<int:id>', methods=['POST'])
def deletar_foto_galeria(id):
    if session.get('user_funcao') != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('galeria'))
        
    conn = get_db_connection()
    foto = conn.execute('SELECT nome_imagem FROM galeria_municipio WHERE id = ?', (id,)).fetchone()
    
    if foto:
        try:
            caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], 'galeria_municipio', foto['nome_imagem'])
            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)
        except Exception as e:
            print(f"Erro ao apagar arquivo físico: {e}")
        
        conn.execute('DELETE FROM galeria_municipio WHERE id = ?', (id,))
        conn.commit()
        flash('Foto excluída com sucesso!')
        
    conn.close()
    return redirect(url_for('galeria'))

# --- ROTAS DE EDIÇÃO E EXCLUSÃO DO DIRETÓRIO ---

@app.route('/admin/deletar_diretorio/<int:id>', methods=['POST'])
def deletar_diretorio(id):
    if session.get('user_funcao') != 'admin':
        flash('Acesso negado.')
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    conn.execute('DELETE FROM galeria_diretorio WHERE diretorio_id = ?', (id,))
    conn.execute('DELETE FROM diretorio WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('Local excluído do sistema com sucesso!')
    return redirect(url_for('admin'))

@app.route('/admin/editar_diretorio/<int:id>', methods=['GET', 'POST'])
def editar_diretorio(id):
    if session.get('user_funcao') != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    
    if request.method == 'POST':
        nome = request.form['nome']
        categoria = request.form['categoria']
        subcategoria = request.form['subcategoria']
        tipo = request.form['tipo']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        horario = request.form['horario']
        descricao = request.form['descricao']
        historia = request.form['historia']
        
        arquivo = request.files.get('imagem')
        
        if arquivo and arquivo.filename != '':
            nome_seguro = secure_filename(arquivo.filename)
            import random
            nome_final = f"{random.randint(1000, 9999)}_{nome_seguro}"
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], 'capas', nome_final))
            
            conn.execute('''
                UPDATE diretorio 
                SET nome=?, categoria=?, subcategoria=?, tipo=?, telefone=?, endereco=?, horario=?, descricao_curta=?, historia_completa=?, imagem_capa=?
                WHERE id=?
            ''', (nome, categoria, subcategoria, tipo, telefone, endereco, horario, descricao, historia, nome_final, id))
        else:
            conn.execute('''
                UPDATE diretorio 
                SET nome=?, categoria=?, subcategoria=?, tipo=?, telefone=?, endereco=?, horario=?, descricao_curta=?, historia_completa=?
                WHERE id=?
            ''', (nome, categoria, subcategoria, tipo, telefone, endereco, horario, descricao, historia, id))
            
        conn.commit()
        conn.close()
        flash('Informações do local atualizadas com sucesso!')
        return redirect(url_for('admin'))

    item = conn.execute('SELECT * FROM diretorio WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if item is None:
        return "Local não encontrado", 404
        
    return render_template('admin_editar.html', item=item)

# --- SISTEMA DE MODERADORES E POSTS FIXADOS ---

@app.route('/toggle_fixar/<int:id>', methods=['POST'])
def toggle_fixar(id):
    if session.get('user_funcao') not in ['admin', 'mod']:
        return "Acesso negado", 403

    conn = get_db_connection()
    post = conn.execute('SELECT fixado FROM postagens WHERE id = ?', (id,)).fetchone()

    if post['fixado'] == 1:
        conn.execute('UPDATE postagens SET fixado = 0 WHERE id = ?', (id,))
        flash('Postagem removida do topo.')
    else:
        fixados_count = conn.execute('SELECT COUNT(*) as qtd FROM postagens WHERE fixado = 1').fetchone()['qtd']
        if fixados_count >= 3:
            flash('Limite atingido: Você só pode fixar 3 postagens no topo. Desfixe uma primeiro.')
        else:
            conn.execute('UPDATE postagens SET fixado = 1 WHERE id = ?', (id,))
            flash('Postagem fixada no topo com sucesso!')

    conn.commit()
    conn.close()
    return redirect(url_for('feed'))

@app.route('/admin/promover/<int:user_id>', methods=['POST'])
def promover_usuario(user_id):
    if session.get('user_funcao') != 'admin':
        return "Acesso negado", 403

    novo_papel = request.form['papel'] 
    conn = get_db_connection()
    conn.execute('UPDATE usuarios SET funcao = ? WHERE id = ?', (novo_papel, user_id))
    conn.commit()
    conn.close()
    
    flash('Nível de acesso do usuário atualizado!')
    return redirect(url_for('admin'))

# --- SISTEMA DE UPVOTES (AJAX / FETCH) ---
@app.route('/upvote/<int:post_id>', methods=['POST'])
def upvote(post_id):
    if 'user_id' not in session:
        return jsonify({'erro': 'Precisa fazer login para votar.'}), 401
        
    user_id = session['user_id']
    conn = get_db_connection()
    
    voto_existente = conn.execute('SELECT * FROM postagens_upvotes WHERE usuario_id = ? AND postagem_id = ?', (user_id, post_id)).fetchone()
    
    if voto_existente:
        conn.execute('DELETE FROM postagens_upvotes WHERE usuario_id = ? AND postagem_id = ?', (user_id, post_id))
        conn.execute('UPDATE postagens SET upvotes = upvotes - 1 WHERE id = ?', (post_id,))
        acao = 'removido'
    else:
        conn.execute('INSERT INTO postagens_upvotes (usuario_id, postagem_id) VALUES (?, ?)', (user_id, post_id))
        conn.execute('UPDATE postagens SET upvotes = upvotes + 1 WHERE id = ?', (post_id,))
        acao = 'adicionado'
        
    conn.commit()
    novo_total = conn.execute('SELECT upvotes FROM postagens WHERE id = ?', (post_id,)).fetchone()['upvotes']
    conn.close()
    
    return jsonify({'upvotes': novo_total, 'acao': acao})

# --- CONTROLE DE AVALIAÇÕES (EDITAR / EXCLUIR) ---

@app.route('/deletar_avaliacao/<int:id>', methods=['POST'])
def deletar_avaliacao(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    av = conn.execute('SELECT * FROM avaliacoes WHERE id = ?', (id,)).fetchone()

    if av:
        if session['user_id'] == av['usuario_id'] or session.get('user_funcao') in ['admin', 'mod']:
            conn.execute('DELETE FROM avaliacoes WHERE id = ?', (id,))
            conn.commit()
            flash('Avaliação excluída com sucesso.')
            
    conn.close()
    return redirect(url_for('detalhes_local', id=av['diretorio_id']))

@app.route('/editar_avaliacao/<int:id>', methods=['GET', 'POST'])
def editar_avaliacao(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    av = conn.execute('SELECT * FROM avaliacoes WHERE id = ?', (id,)).fetchone()

    if not av or session['user_id'] != av['usuario_id']:
        conn.close()
        flash('Acesso negado. Você só pode editar suas próprias avaliações.')
        return redirect(url_for('diretorio'))

    if request.method == 'POST':
        nota = request.form.get('nota')
        comentario = request.form.get('comentario')
        
        conn.execute('UPDATE avaliacoes SET nota = ?, comentario = ? WHERE id = ?', (nota, comentario, id))
        conn.commit()
        conn.close()
        flash('Sua avaliação foi atualizada!')
        return redirect(url_for('detalhes_local', id=av['diretorio_id']))

    local = conn.execute('SELECT nome FROM diretorio WHERE id = ?', (av['diretorio_id'],)).fetchone()
    conn.close()
    
    return render_template('editar_avaliacao.html', av=av, local=local)

# --- CONTROLE DE POSTAGENS DO FEED (EDITAR / EXCLUIR) ---

@app.route('/deletar_postagem/<int:id>', methods=['POST'])
def deletar_postagem(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    post = conn.execute('SELECT * FROM postagens WHERE id = ?', (id,)).fetchone()

    if post:
        if session['user_id'] == post['usuario_id'] or session.get('user_funcao') in ['admin', 'mod']:
            conn.execute('DELETE FROM postagens_upvotes WHERE postagem_id = ?', (id,))
            conn.execute('DELETE FROM postagens WHERE id = ?', (id,))
            conn.commit()
            flash('Publicação excluída com sucesso.')
            
    conn.close()
    return redirect(url_for('feed'))

@app.route('/editar_postagem/<int:id>', methods=['GET', 'POST'])
def editar_postagem(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    post = conn.execute('SELECT * FROM postagens WHERE id = ?', (id,)).fetchone()

    if not post or session['user_id'] != post['usuario_id']:
        conn.close()
        flash('Acesso negado. Você só pode editar suas próprias publicações.')
        return redirect(url_for('feed'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        conteudo = request.form['conteudo']
        categoria = request.form['categoria']
        
        conn.execute('UPDATE postagens SET titulo = ?, conteudo = ?, categoria = ? WHERE id = ?', 
                     (titulo, conteudo, categoria, id))
        conn.commit()
        conn.close()
        flash('Sua publicação foi atualizada!')
        return redirect(url_for('feed'))

    conn.close()
    return render_template('editar_postagem.html', post=post)

# --- CONTROLE DE ANÚNCIOS / MARKETPLACE (EDITAR / EXCLUIR) ---

@app.route('/deletar_anuncio/<int:id>', methods=['POST'])
def deletar_anuncio(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    anuncio = conn.execute('SELECT * FROM marketplace WHERE id = ?', (id,)).fetchone()

    if anuncio:
        if session['user_id'] == anuncio['usuario_id'] or session.get('user_funcao') in ['admin', 'mod']:
            import os
            # Tenta apagar imagens antigas (se existirem e não forem a default)
            for img_col in ['imagem', 'imagem1', 'imagem2']:
                try:
                    img_name = anuncio.get(img_col)
                    if img_name and img_name != 'default_produto.jpg':
                        caminho = os.path.join(app.config['UPLOAD_FOLDER'], 'marketplace', img_name)
                        if os.path.exists(caminho):
                            os.remove(caminho)
                except Exception:
                    pass
            
            conn.execute('DELETE FROM marketplace WHERE id = ?', (id,))
            conn.commit()
            flash('Anúncio excluído com sucesso.')
            
    conn.close()
    return redirect(url_for('marketplace'))

@app.route('/editar_anuncio/<int:id>', methods=['GET', 'POST'])
def editar_anuncio(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    anuncio = conn.execute('SELECT * FROM marketplace WHERE id = ?', (id,)).fetchone()

    if not anuncio or session['user_id'] != anuncio['usuario_id']:
        conn.close()
        flash('Acesso negado. Você só pode editar seus próprios anúncios.')
        return redirect(url_for('marketplace'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        preco = request.form['preco']
        categoria = request.form['categoria']
        contato = request.form['contato']
        
        # Opcional: Aqui poderíamos expandir no futuro para editar as fotos também!
        
        conn.execute('''
            UPDATE marketplace 
            SET titulo=?, descricao=?, preco=?, categoria=?, contato=? 
            WHERE id=?
        ''', (titulo, descricao, preco, categoria, contato, id))
            
        conn.commit()
        conn.close()
        flash('Seu anúncio foi atualizado!')
        return redirect(url_for('marketplace'))

    conn.close()
    return render_template('editar_anuncio.html', anuncio=anuncio)

# --- SISTEMA DE PERFIL E MEMORIAL DE FOTOS ---

@app.route('/perfil/<int:id>', methods=['GET', 'POST'])
def perfil(id):
    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM usuarios WHERE id = ?', (id,)).fetchone()
    
    if not usuario:
        conn.close()
        flash('Usuário não encontrado.')
        return redirect(url_for('feed'))
        
    if request.method == 'POST':
        if session.get('user_id') != id:
            flash('Acesso negado. Você não pode alterar o perfil de outra pessoa.')
            return redirect(url_for('perfil', id=id))
            
        acao = request.form.get('acao')
        
        if acao == 'atualizar_nome':
            novo_nome = request.form.get('nome')
            conn.execute('UPDATE usuarios SET nome = ? WHERE id = ?', (novo_nome, id))
            conn.commit()
            session['user_nome'] = novo_nome 
            flash('Seu nome foi atualizado com sucesso!')
            
        elif acao == 'nova_foto':
            titulo = request.form.get('titulo')
            arquivo = request.files.get('imagem')
            
            if arquivo and arquivo.filename != '':
                nome_seguro = secure_filename(arquivo.filename)
                import random
                nome_final = f"memorial_{id}_{random.randint(1000, 9999)}_{nome_seguro}"
                
                pasta = os.path.join(app.config['UPLOAD_FOLDER'], 'galeria_usuarios')
                os.makedirs(pasta, exist_ok=True)
                arquivo.save(os.path.join(pasta, nome_final))
                
                conn.execute('INSERT INTO galeria_usuarios (usuario_id, titulo, nome_imagem) VALUES (?, ?, ?)',
                             (id, titulo, nome_final))
                conn.commit()
                flash('Foto adicionada ao seu Memorial de Moçâmedes!')
                
        return redirect(url_for('perfil', id=id))

    fotos = conn.execute('SELECT * FROM galeria_usuarios WHERE usuario_id = ? ORDER BY data_criacao DESC', (id,)).fetchall()
    conn.close()
    
    return render_template('perfil.html', usuario=usuario, fotos=fotos)

@app.route('/deletar_foto_memorial/<int:id>', methods=['POST'])
def deletar_foto_memorial(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    foto = conn.execute('SELECT * FROM galeria_usuarios WHERE id = ?', (id,)).fetchone()
    
    if foto and (session['user_id'] == foto['usuario_id'] or session.get('user_funcao') in ['admin', 'mod']):
        import os
        try:
            caminho = os.path.join(app.config['UPLOAD_FOLDER'], 'galeria_usuarios', foto['nome_imagem'])
            if os.path.exists(caminho):
                os.remove(caminho)
        except: pass
            
        conn.execute('DELETE FROM galeria_usuarios WHERE id = ?', (id,))
        conn.commit()
        flash('Foto removida do memorial.')
        
    conn.close()
    return redirect(request.referrer or url_for('feed'))

if __name__ == '__main__':
    app.run(debug=True)