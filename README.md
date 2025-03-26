# 📊 Finance Dashboard - Backend

API REST desenvolvida com **FastAPI** para consultar cotações de ações e moedas, registrar histórico de pesquisas e retornar dados históricos para exibição em gráfico. 

---

## 🔎 Visão Geral
Este projeto faz parte de um MVP para consulta de dados financeiros e foi desenvolvido conforme o Cenário 1.1 proposto na disciplina. Ele fornece uma API com 6 endpoints REST (GET, POST, PUT, DELETE) para acesso e gestão de dados.

---

## 🚀 Tecnologias Utilizadas
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/) - servidor ASGI para execução
- [yFinance](https://pypi.org/project/yfinance/) - dados de ações
- [AwesomeAPI](https://docs.awesomeapi.com.br/api-de-moedas) - dados de moedas
- SQLite - banco de dados local para persistência
- Docker

---

## ⚖️ Instalação e Execução (via Docker)

> Requisitos: Docker e Docker Compose instalados

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/finance-dashboard-mvp.git
cd finance-dashboard-mvp
```

2. Rode a aplicação via Docker Compose:
```bash
docker-compose up --build
```

3. A API ficará disponível em:
```
http://localhost:8000
```

4. Documentação Swagger:
```
http://localhost:8000/docs
```

---

## 🔍 Endpoints Disponíveis

### GET `/consulta`
Consulta preço e variação atual de ação ou moeda.
```bash
/consulta?tipo=acao&codigo=AAPL
```

### GET `/grafico`
Retorna histórico de fechamento dos últimos 90 dias.
```bash
/grafico?tipo=acao&codigo=AAPL
```

### GET `/historico`
Lista de todas as consultas feitas.

### POST `/historico`
Insere manualmente uma consulta (para testes ou preenchimento).
```json
{
  "tipo": "moeda",
  "codigo": "USDBRL",
  "nome": "Dólar/Real",
  "preco": "R$ 5,69",
  "variacao": "-0,34"
}
```

### PUT `/historico/{item_id}`
Atualiza um item do histórico existente.

### DELETE `/historico/{item_id}`
Remove um item do histórico.

---

## 📅 Exemplo de Fluxograma da Arquitetura

![Arquitetura](./docs/fluxo-arquitetura-backend.png)

> O backend se comunica com APIs externas (yFinance, AwesomeAPI), processa os dados, salva no SQLite e expõe endpoints RESTful para o frontend.

---

## ✍️ Autor
**Cristopher Aquino**  
[LinkedIn](https://www.linkedin.com/in/%F0%9F%8E%AF-cristopher-aquino-4992b251/)  
Telefone: (21) 98005-9430
