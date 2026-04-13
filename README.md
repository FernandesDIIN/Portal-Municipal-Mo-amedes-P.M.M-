# Portal Municipal de Moçâmedes (P.M.M)

O Portal Municipal de Moçâmedes é uma plataforma web desenvolvida como Projeto de Aptidão Profissional (PAP) / Trabalho de Conclusão de Curso. 

O objetivo central do projeto é atuar como o guia definitivo de bolso para o município (província do Namibe, Angola). A plataforma foi construída para responder de forma rápida e clara à pergunta diária dos cidadãos: "Onde fica e como chego lá?", centralizando endereços, contactos e informações comunitárias num único ambiente digital seguro e organizado.

## Principais Funcionalidades

O sistema foi arquitetado para oferecer uma experiência focada na utilidade pública e na navegação urbana:

* Diretório Municipal: Um catálogo interativo e categorizado de instituições públicas, hospitais, escolas e comércio local, contendo informações exatas de contacto e localização.
* Sistema de Avaliações: Os cidadãos podem classificar os locais do diretório de 1 a 5 estrelas e deixar comentários, ajudando a criar um padrão de qualidade no atendimento local.
* Mural da Comunidade (Feed): Um espaço para partilha de notícias, eventos e avisos de utilidade pública. Utiliza um algoritmo de relevância dinâmico que destaca as postagens com base no número de votos (Upvotes) e no tempo decorrido desde a publicação.
* Galeria e Memorial Cidadão: Uma galeria global para preservar a memória e a beleza de Moçâmedes, além de perfis individuais onde os cidadãos possuem o seu próprio memorial fotográfico.
* Moderação e Segurança: Sistema de controlo de acesso baseado em níveis (Cidadão, Moderador e Administrador), com um painel de gestão exclusivo para garantir a veracidade dos locais e a segurança do conteúdo.

## Tecnologias Utilizadas

* Back-end: Python 3, Flask (Microframework Web)
* Banco de Dados: SQLite3 (Relacional, leve e embutido)
* Front-end: HTML5, CSS3 puro (Vanilla), JavaScript (para interações dinâmicas e assíncronas)
* Template Engine: Jinja2
* Integração Externa: API do UI-Avatars para geração automática de imagens de perfil

## Como Executar o Projeto Localmente

Siga os passos abaixo para preparar o ambiente e rodar o Portal na sua máquina:

### 1. Pré-requisitos
Certifique-se de ter o Python 3 instalado no seu computador.

### 2. Clonar o Repositório
Abra o terminal e execute:
git clone https://github.com/FernandesDIIN/Portal-Municipal-P.M.-Mocamedes.git
cd Portal-Municipal-P.M.-Mocamedes

### 3. Criar e Ativar o Ambiente Virtual
No Windows:
python -m venv venv
venv\Scripts\activate

No Linux ou Mac:
python3 -m venv venv
source venv/bin/activate

### 4. Instalar as Dependências
Certifique-se de que possui o arquivo `requirements.txt` na raiz do projeto. Para instalar todas as bibliotecas necessárias, execute o comando abaixo no seu terminal:

```bash
pip install -r requirements.txt
```

### 5. Inicializar o Banco de Dados
Caso seja a primeira execução e precise configurar as tabelas e perfis, execute os scripts de preparação:
python atualizar_upvotes.py
python corrigir_avaliacoes.py
python atualizar_perfil.py

### 6. Executar a Aplicação
Inicie o servidor local com o comando:
python app.py

O servidor estará a rodar. Abra o seu navegador e aceda a: http://127.0.0.1:5000

## Estrutura do Projeto

portal_mocamedes/
|-- app.py                   (Cérebro do sistema: Rotas e Lógica Python)
|-- banco.db                 (Banco de Dados SQLite gerado automaticamente)
|-- static/                  (Arquivos públicos)
|   |-- css/                 (Folha de estilos principal - style.css)
|   |-- img/                 (Imagens fixas de layout)
|   |-- uploads/             (Arquivos e fotos enviadas pelos utilizadores)
|-- templates/               (Interfaces HTML)
|   |-- base.html            (Estrutura mestre de navegação)
|   |-- index.html           (Página Inicial)
|   |-- diretorio.html       (Catálogo da cidade)
|   |-- feed.html            (Mural de notícias e eventos)
|   |-- perfil.html          (Página de utilizador e memorial)
|   |-- admin.html           (Painel de gestão)
|-- README.md                (Documentação)

## Acesso Administrativo (Testes)

Para avaliar as funcionalidades do Painel de Gestão, utilize as seguintes credenciais:
* Email: admin@mocamedes.ao
* Senha: admin123

## Autor

Desenvolvido com dedicação por Tchivangulula D. Joao Fernandes [FernandesDIIN] como Projeto de Aptidão Profissional (PAP) do ensino médio. Sinta-se à vontade para contribuir, abrir issues ou explorar o código.

Nota do Autor: Assistam à série Andor, é uma experiência incrível!