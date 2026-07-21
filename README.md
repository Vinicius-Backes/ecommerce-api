# E-commerce API

API REST de um e-commerce simplificado, construída com **FastAPI**, **SQLAlchemy** e **PostgreSQL**.

## Funcionalidades implementadas

- Autenticação com JWT (registro e login)
- Perfis de usuário comum e administrador
- CRUD de categorias (admin)
- CRUD de produtos com filtros e paginação (admin cria/edita/remove; leitura pública)
- Carrinho de compras com validação de estoque
- Checkout: conversão do carrinho em pedido, com baixa automática de estoque
- Listagem e gestão de pedidos (usuário e admin)

## Como rodar com Docker (recomendado)

```bash
cp .env.example .env
docker compose up --build
```

A API estará disponível em `http://localhost:8000` e a documentação interativa (Swagger) em `http://localhost:8000/docs`.

## Como rodar localmente sem Docker

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# edite o .env com a URL do seu Postgres local

uvicorn app.main:app --reload
```

## Criando o primeiro usuário administrador

Por padrão, todo usuário criado via `/auth/register` é `is_admin=False`. Para criar um admin, promova um usuário direto no banco:

```sql
UPDATE users SET is_admin = true WHERE email = 'seu-email@exemplo.com';
```

## Estrutura do projeto

```
app/
├── main.py          # Ponto de entrada
├── config.py        # Configurações via .env
├── database.py       # Conexão com o banco
├── models/           # Tabelas (SQLAlchemy)
├── schemas/           # Validação de entrada/saída (Pydantic)
├── routers/           # Endpoints da API
├── services/           # Regras de negócio
└── core/               # Segurança e dependências (JWT, permissões)
```

## Próximos passos sugeridos

- [ ] Migrações com Alembic em vez de `create_all`
- [ ] Integração de pagamento (Stripe/Mercado Pago) em modo sandbox
- [ ] Testes cobrindo carrinho e checkout
- [ ] Rate limiting (ex: `slowapi`)
- [ ] Deploy em Render/Railway/Fly.io

## Endpoints principais

| Método | Rota | Descrição | Acesso |
|---|---|---|---|
| POST | `/auth/register` | Cria usuário | Público |
| POST | `/auth/login` | Login (retorna JWT) | Público |
| GET | `/users/me` | Dados do usuário logado | Autenticado |
| GET | `/products/` | Lista produtos (filtros/paginação) | Público |
| POST | `/products/` | Cria produto | Admin |
| GET | `/cart/` | Vê carrinho | Autenticado |
| POST | `/cart/items` | Adiciona item ao carrinho | Autenticado |
| POST | `/orders/checkout` | Fecha pedido a partir do carrinho | Autenticado |
| GET | `/orders/` | Lista meus pedidos | Autenticado |
| GET | `/orders/admin/all` | Lista todos os pedidos | Admin |