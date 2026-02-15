-- LIMPEZA GERAL (Reseta o banco)
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS postagens;
DROP TABLE IF EXISTS diretorio;
DROP TABLE IF EXISTS marketplace;
DROP TABLE IF EXISTS comentarios;
DROP TABLE IF EXISTS avaliacoes;

-- 1. TABELA DE USUÁRIOS
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE,    -- Não é mais NOT NULL (pode ser vazio)
    telefone TEXT UNIQUE, -- Novo campo de login
    senha TEXT NOT NULL,
    funcao TEXT DEFAULT 'cidadao',
    foto_perfil TEXT DEFAULT 'default_profile.png',
    bio TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABELA DO DIRETÓRIO (Locais e Serviços Fixos)
CREATE TABLE diretorio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,    -- Ex: Saúde, Educação, Comércio
    subcategoria TEXT,          -- Ex: Farmácia, Hotel, Escola Primária
    tipo TEXT NOT NULL,         -- 'Publico' ou 'Privado'
    endereco TEXT,
    telefone TEXT,
    horario TEXT,               -- Ex: "08:00 - 18:00"
    descricao_curta TEXT,       -- Resumo para o card
    historia_completa TEXT,     -- Texto longo para a página de detalhes
    imagem_capa TEXT DEFAULT 'default_cover.jpg',
    media_avaliacao REAL DEFAULT 0, -- Média de estrelas (será calculado na Fase 3)
    autor_id INTEGER,           -- Quem cadastrou (geralmente admin)
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (autor_id) REFERENCES usuarios (id)
);

-- 3. TABELA DE MARKETPLACE (Motor de Emprego e Vendas)
CREATE TABLE marketplace (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT NOT NULL,
    tipo_anuncio TEXT NOT NULL, -- 'oferta' (eu faço) ou 'procura' (preciso de)
    categoria TEXT NOT NULL,    -- Ex: Serviços Domésticos, Vendas, Transporte
    preco TEXT,                 -- Opcional
    contato TEXT NOT NULL,      -- Telefone ou Email para contato
    imagem TEXT,                -- Foto do produto ou serviço
    usuario_id INTEGER NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);

-- 4. TABELA DE POSTAGENS (Feed de Notícias e Social)
CREATE TABLE postagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT,                -- Pode ser vazio se for só um desabafo social
    conteudo TEXT NOT NULL,
    categoria TEXT NOT NULL,    -- Notícia, Social, Utilidade Pública
    imagem TEXT,
    usuario_id INTEGER NOT NULL,
    likes_count INTEGER DEFAULT 0,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);

-- 5. TABELA DE AVALIAÇÕES (Para a Fase 3, mas já deixamos pronta)
CREATE TABLE avaliacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    diretorio_id INTEGER NOT NULL,
    estrelas INTEGER NOT NULL, -- 1 a 5
    comentario TEXT,
    data_avaliacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === DADOS DE EXEMPLO (SEED) ===

-- Admin Principal
INSERT INTO usuarios (nome, email, senha, funcao, bio) 
VALUES ('Administrador Portal', 'admin@mocamedes.ao', 'admin123', 'admin', 'Gerente oficial do portal da cidade.');

-- Cidadão Exemplo
INSERT INTO usuarios (nome, email, senha, funcao, bio) 
VALUES ('João Silva', 'joao@email.com', '123456', 'cidadao', 'Morador do Bairro 5 de Abril.');

-- Exemplo Diretório: Hospital (Público)
INSERT INTO diretorio (nome, categoria, subcategoria, tipo, endereco, telefone, horario, descricao_curta, historia_completa)
VALUES (
    'Hospital Provincial do Namibe', 
    'Saúde', 'Hospital Geral', 'Publico',
    'Rua da Saúde, Centro', '+244 923 000 000', '24 Horas',
    'Unidade de referência provincial.',
    'Fundado para atender toda a província, o hospital conta com diversas especialidades...'
);

-- Exemplo Diretório: Hotel (Privado)
INSERT INTO diretorio (nome, categoria, subcategoria, tipo, endereco, telefone, horario, descricao_curta)
VALUES (
    'Hotel Infotur', 
    'Comércio', 'Hotelaria', 'Privado',
    'Aeroporto Yuri Gagarin', '+244 923 111 222', 'Aberto Sempre',
    'Conforto e qualidade para visitantes.'
);

-- Exemplo Marketplace: Oferta de Serviço
INSERT INTO marketplace (titulo, descricao, tipo_anuncio, categoria, contato, usuario_id)
VALUES ('Eletricista Profissional', 'Faço instalações residenciais e prediais. 10 anos de experiência.', 'oferta', 'Serviços', '+244 900 000 000', 2);

-- Exemplo Postagem: Notícia
INSERT INTO postagens (titulo, conteudo, categoria, usuario_id)
VALUES ('Campanha de Vacinação', 'Amanhã começa a vacinação infantil em todos os postos de saúde.', 'Utilidade Pública', 1);