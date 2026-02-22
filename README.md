📊 Finance Household API

Sistema backend para gestão financeira compartilhada (casal/household), com integração ao Google Sheets como camada de persistência (MVP).

📌 Objetivo

Desenvolver uma API financeira capaz de:

Gerenciar orçamento mensal

Controlar despesas

Integrar lista de compras ao planejamento financeiro

Calcular projeção financeira automática

Permitir uso compartilhado por múltiplos usuários (household)

O projeto foi estruturado com foco em:

Separação clara de responsabilidades

Regra de negócio isolada

Facilidade de troca da camada de persistência (Sheets → PostgreSQL)

🏗️ Arquitetura

O projeto segue arquitetura em camadas:

Controller → Service → Repository → Infra

🔹 Controller

Responsável por:

Receber requisições

Validar dados

Chamar serviços

Retornar respostas

🔹 Service

Responsável por:

Regra de negócio

Cálculo financeiro

Orquestração de fluxos

🔹 Repository

Responsável por:

Comunicação com Google Sheets

Conversão de dados externos para modelos internos

🔹 Infra

Responsável por:

Integrações externas

Configuração de API Google

Autenticação

📂 Estrutura de Pastas
src/
 ├── modules/
 │    ├── finance/
 │    ├── shopping/
 │    ├── expenses/
 │    ├── categories/
 │    ├── budget/
 │
 ├── infra/
 │    ├── sheets/
 │    ├── auth/
 │    └── config/
 │
 ├── core/
 │    ├── errors/
 │    ├── middleware/
 │    └── utils/
 │
 ├── app.ts
 └── server.ts
🧠 Regra de Negócio Principal

O sistema calcula:

Saldo atual

Total gasto

Total no carrinho

Saldo projetado

Percentual comprometido

Verificação de meta de economia

Fórmula base
saldoAtual = renda - totalGasto
saldoProjetado = saldoAtual - totalCarrinho
percentualComprometido = (gasto + carrinho) / renda
🛒 Integração Lista ↔ Financeiro

Itens com status CART entram na projeção.

Itens com status PURCHASED:

Geram automaticamente uma despesa.

Atualizam o cálculo financeiro.

📊 Persistência (MVP)

A aplicação utiliza Google Sheets como banco de dados temporário.

Abas esperadas na planilha:
Expenses

id

description

value

category

date

origin

Shopping

id

name

quantity

estimatedPrice

category

status

Categories

id

name

monthlyLimit

Budget

income

savingsGoal

🔐 Integração com Google Sheets

O projeto utiliza:

Google Sheets API

Service Account

Passos necessários:

Criar projeto no Google Cloud

Ativar Google Sheets API

Criar Service Account

Baixar credenciais JSON

Compartilhar planilha com o e-mail da Service Account

🚀 Como Rodar o Projeto
1️⃣ Instalar dependências
npm install
2️⃣ Configurar variáveis de ambiente

Criar .env:

PORT=3000
GOOGLE_SHEETS_ID=your_sheet_id
GOOGLE_SERVICE_ACCOUNT_EMAIL=your_service_account_email
GOOGLE_PRIVATE_KEY=your_private_key
3️⃣ Rodar em desenvolvimento
npm run dev
🧪 Testes

O motor financeiro deve possuir testes unitários cobrindo:

Cenário normal

Estouro de orçamento

Meta de economia não atingida

Carrinho vazio

Renda zero

📈 Roadmap
MVP

 CRUD Categorias

 CRUD Despesas

 CRUD Lista de Compras

 Motor de projeção financeira

 Integração automática PURCHASED → Expense

Próximas versões

 Autenticação Google OAuth

 Multi-household

 Cache interno

 Dashboard estatístico

 Exportação PDF

 Migração para PostgreSQL

 Deploy em produção

⚠️ Cuidados Técnicos

Não misturar regra de negócio no controller

Validar todas as entradas (Zod)

Não confiar no front-end

Centralizar cálculo financeiro

Evitar múltiplas chamadas desnecessárias ao Google Sheets

Tratar erros da API Google adequadamente

🧩 Possível Evolução Arquitetural

O projeto foi desenhado para permitir troca da camada de persistência:

SheetsFinanceRepository (MVP)

PostgresFinanceRepository (futuro)

Isso evita acoplamento direto à tecnologia de armazenamento.

📚 Boas Práticas Aplicadas

Separação de camadas

Tipagem forte com TypeScript

DTOs definidos

Regras isoladas em services

Estrutura modular

Commits semânticos

🎯 Objetivo de Portfólio

Este projeto demonstra:

Modelagem de regra de negócio real

Integração com API externa

Organização arquitetural

Planejamento de evolução

Pensamento orientado a domínio
