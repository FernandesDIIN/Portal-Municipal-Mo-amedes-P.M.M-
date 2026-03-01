# 🇦🇴 Portal Municipal

O **Portal Mucicipal Moçâmedes** é uma plataforma web desenvolvida como Projeto de Aptitidão Profissional (PAP). O objetivo do projeto é atuar como um *hub* centralizado digital para o município de Moçâmedes (província do Namibe, Angola), conectando cidadãos, turistas e comércio local em um único espaço interativo.

## 🚀 Principais Funcionalidades

O sistema foi arquitetado em módulos para oferecer uma experiência completa de comunidade:

* **📖 Diretório de Locais e Serviços:** Um catálogo interativo de instituições públicas, hospitais, escolas e pontos turísticos. Conta com informações de contato, localização e galeria de imagens.
* **⭐ Sistema de Avaliações:** Usuários podem classificar locais de 1 a 5 estrelas e deixar comentários (com cálculo automático de média e proteção contra spam).
* **🗣️ Feed Comunitário (Relevância Dinâmica):** Um mural de notícias e avisos equipado com um algoritmo de decadência temporal (estilo Reddit). Posts ganham destaque baseados em *Upvotes* e no tempo de publicação.
* **🛒 Classificados / Marketplace:** Espaço dedicado para os cidadãos anunciarem compra, venda, imóveis e prestação de serviços.
* **👤 Perfis e Memorial (Galeria Cidadã):** Cada usuário possui um perfil público gerado dinamicamente com avatares automáticos (UI-Avatars) e um "Memorial" para postar fotos das suas vivências na cidade.
* **🛡️ Moderação e Segurança (RBAC):** Sistema robusto de Controle de Acesso Baseado em Cargos (Cidadão, Moderador e Administrador), permitindo edição própria e moderação de conteúdo impróprio em todo o site.

## 🛠️ Tecnologias Utilizadas

* **Back-end:** Python 3, Flask (Framework Web)
* **Banco de Dados:** SQLite3 (Relacional, leve e embutido)
* **Front-end:** HTML5, CSS3, Vanilla JavaScript (AJAX/Fetch API para interações sem recarregar a página)
* **Template Engine:** Jinja2
* **Integração Externa:** UI-Avatars API

## ⚙️ Como Executar o Projeto Localmente

Siga os passos abaixo para rodar o Portal Moçâmedes na sua máquina:

### 1. Pré-requisitos
Certifique-se de ter o **Python** instalado na sua máquina.

### 2. Clonar o Repositório
```bash
git clone [https://github.com/FernandesDIIN/Portal-Municipal-P.M.-Mocamedes.git)
cd portal-mocamedes
```

### 3. Criar e Ativar o Ambiente Virtual (Recomendado)
```bash
# No Windows
python -m venv venv
venv\Scripts\activate

# No Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar as Dependências
(Nota: Certifique-se de criar um arquivo requirements.txt com as bibliotecas, ou instale o Flask manualmente).
```bash
pip install -r requirements.txt
ou
pip install flask werkzeug
```

### 5. Inicializar o Banco de Dados
Para criar as tabelas necessárias, execute os scripts de banco na raiz do projeto:
```bash
python atualizar_upvotes.py
python corrigir_avaliacoes.py
python atualizar_perfil.py
```

### 6. Executar a Aplicação
```bash
python app.py
```
O servidor será iniciado. Acesse no seu navegador: http://127.0.0.1:5000

📂 Estrutura do Projeto
```Plaintext
portal_mocamedes/
│
├── app.py                   # Arquivo principal (Rotas e Lógica de Negócio)
├── banco.db                 # Banco de Dados SQLite (gerado automaticamente)
├── static/                  # Arquivos estáticos
│   ├── css/                 # Folhas de estilo (style.css)
│   ├── img/                 # Imagens fixas do layout
│   └── uploads/             # Imagens enviadas pelos usuários (capas, galeria, perfil)
│
├── templates/               # Páginas em HTML (Jinja2)
│   ├── base.html            # Estrutura mestre (Header e Footer)
│   ├── index.html           # Página Inicial
│   ├── diretorio.html       # Catálogo de locais
│   ├── feed.html            # Mural da comunidade
│   ├── perfil.html          # Memorial do usuário
│   └── ...                  # Outras páginas e formulários CRUD
│
└── README.md                # Documentação do projeto
```

ADM ACESS
```text
admin: admin@mocamedes.ao
senha: admin123
```

👨‍💻 Autor
Desenvolvido com dedicação por Tchivangulula D. Joao Fernandes [FernandesDIIN] como Trabalho de Conclusão de Curso (TCC) do ensino medio.
Sinta-se à vontade para contribuir, abrir issues ou enviar pull requests!
OBRIGADOO, Assistam Andor, que experiencia incrivel!