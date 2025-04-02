from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
import requests
from datetime import datetime
import sqlite3

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo para validação dos dados
class HistoricoItem(BaseModel):
    data_consulta: str
    tipo: str
    codigo: str
    nome: str
    preco: str
    variacao: str

# Banco
def init_db():
    conn = sqlite3.connect("stocks.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_consulta TEXT,
            tipo TEXT,
            codigo TEXT,
            nome TEXT,
            preco TEXT,
            variacao TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.get("/consulta")
def consulta(tipo: str = Query(...), codigo: str = Query(...)):
    codigo = codigo.upper()
    if tipo == "acao" and not codigo.endswith(".SA") and not codigo.isalpha():
        codigo += ".SA"

    try:
        if tipo == "acao":
            ticker = yf.Ticker(codigo)
            info = ticker.info or {}
            nome = info.get("shortName") or info.get("longName")
            preco = info.get("currentPrice")
            variacao = info.get("regularMarketChangePercent")
        elif tipo == "moeda":
            url = f"https://economia.awesomeapi.com.br/json/last/{codigo}"
            response = requests.get(url)
            if response.status_code != 200:
                return {"erro": "Código de moeda inválido ou não encontrado."}
            json_data = response.json()
            key = list(json_data.keys())[0]
            data = json_data[key]
            preco = float(data.get("bid"))
            variacao = float(data.get("pctChange"))
            nome = data.get("name")
        else:
            return {"erro": "Tipo inválido. Use 'acao' ou 'moeda'"}

        preco_formatado = (
            f"{preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if tipo == "acao"
            else f"{preco:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        variacao_formatada = f"{variacao:.2f}".replace(".", ",")
        data_atual = datetime.now().strftime("%d/%m/%Y")

        conn = sqlite3.connect("stocks.db")
        c = conn.cursor()
        c.execute(
            'INSERT INTO historico (data_consulta, tipo, codigo, nome, preco, variacao) VALUES (?, ?, ?, ?, ?, ?)',
            (data_atual, tipo, codigo, nome.upper(), preco_formatado, variacao_formatada),
        )
        conn.commit()
        conn.close()

        return {
            "tipo": tipo,
            "codigo": codigo,
            "nome": nome.upper(),
            "preco": preco_formatado,
            "variacao": variacao_formatada,
        }

    except Exception as e:
        return {"erro": f"Erro ao buscar dados: {str(e)}"}

@app.get("/historico")
def get_historico():
    conn = sqlite3.connect("stocks.db")
    c = conn.cursor()
    c.execute("SELECT * FROM historico ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "data_consulta": row[1],
            "tipo": row[2],
            "codigo": row[3],
            "nome": row[4],
            "preco": row[5],
            "variacao": row[6],
        }
        for row in rows
    ]

@app.post("/historico")
def adicionar_item(item: HistoricoItem):
    conn = sqlite3.connect("stocks.db")
    c = conn.cursor()
    c.execute(
        'INSERT INTO historico (data_consulta, tipo, codigo, nome, preco, variacao) VALUES (?, ?, ?, ?, ?, ?)',
        (item.data_consulta, item.tipo, item.codigo, item.nome, item.preco, item.variacao),
    )
    conn.commit()
    item_id = c.lastrowid
    conn.close()
    return {"id": item_id, **item.dict()}

@app.put("/historico/{item_id}")
def atualizar_item(item_id: int, novos_dados: HistoricoItem):
    conn = sqlite3.connect("stocks.db")
    c = conn.cursor()
    c.execute(
        'UPDATE historico SET data_consulta = ?, tipo = ?, codigo = ?, nome = ?, preco = ?, variacao = ? WHERE id = ?',
        (
            novos_dados.data_consulta,
            novos_dados.tipo,
            novos_dados.codigo,
            novos_dados.nome,
            novos_dados.preco,
            novos_dados.variacao,
            item_id,
        ),
    )
    conn.commit()
    conn.close()
    return {"mensagem": f"Item com ID {item_id} atualizado com sucesso"}

@app.delete("/historico/{item_id}")
def deletar_item(item_id: int):
    conn = sqlite3.connect("stocks.db")
    c = conn.cursor()
    c.execute("DELETE FROM historico WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"mensagem": f"Item com ID {item_id} deletado com sucesso"}



















