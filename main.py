from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import requests
from datetime import datetime
from typing import List, Optional

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

historico_consultas = []

@app.get("/consulta")
def consulta(tipo: str = Query(...), codigo: str = Query(...)):
    codigo = codigo.upper()
    if tipo == "acao" and not codigo.endswith(".SA") and not codigo.isalpha():
        codigo += ".SA"

    if tipo == "acao":
        try:
            ticker = yf.Ticker(codigo)
            info = ticker.info or {}
            nome = info.get("shortName") or info.get("longName")
            preco = info.get("currentPrice")
            variacao = info.get("regularMarketChangePercent")

            if nome is None or preco is None:
                return {"erro": "Código de ação inválido ou sem dados disponíveis."}

            if isinstance(preco, float):
                preco = f"{preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if isinstance(variacao, float):
                variacao = f"{variacao:.2f}".replace(".", ",")

            data_atual = datetime.now().strftime("%d/%m/%Y")
            historico_consultas.insert(0, {
                "id": len(historico_consultas) + 1,
                "data_consulta": data_atual,
                "tipo": tipo,
                "codigo": codigo,
                "nome": nome.upper(),
                "preco": preco,
                "variacao": variacao
            })

            return {
                "tipo": tipo,
                "codigo": codigo,
                "nome": nome.upper(),
                "preco": preco,
                "variacao": variacao
            }
        except Exception as e:
            return {"erro": f"Erro ao buscar ação: {str(e)}"}

    elif tipo == "moeda":
        try:
            url = f"https://economia.awesomeapi.com.br/json/last/{codigo}"
            response = requests.get(url)
            if response.status_code != 200:
                return {"erro": "Código de moeda inválido ou não encontrado."}
            json_data = response.json()
            if not json_data:
                return {"erro": "Código de moeda inválido ou não encontrado."}
            key = list(json_data.keys())[0]
            data = json_data[key]
            preco = data.get("bid")
            variacao = data.get("pctChange")
            nome = data.get("name")

            if preco is None or nome is None:
                return {"erro": "Código de moeda inválido ou não encontrado."}

            preco = f"{float(preco):,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
            variacao = variacao.replace(".", ",")

            data_atual = datetime.now().strftime("%d/%m/%Y")
            historico_consultas.insert(0, {
                "id": len(historico_consultas) + 1,
                "data_consulta": data_atual,
                "tipo": tipo,
                "codigo": codigo,
                "nome": nome.upper(),
                "preco": preco,
                "variacao": variacao
            })

            return {
                "tipo": tipo,
                "codigo": codigo,
                "nome": nome.upper(),
                "preco": preco,
                "variacao": variacao
            }
        except Exception as e:
            return {"erro": f"Erro ao buscar moeda: {str(e)}"}

    return {"erro": "Tipo inválido. Use 'acao' ou 'moeda'"}

@app.get("/historico")
def historico():
    return historico_consultas

@app.post("/historico")
def adicionar_item(item: dict):
    item["id"] = len(historico_consultas) + 1
    historico_consultas.append(item)
    return item

@app.put("/historico/{item_id}")
def atualizar_item(item_id: int, novos_dados: dict):
    for i, item in enumerate(historico_consultas):
        if item["id"] == item_id:
            historico_consultas[i].update(novos_dados)
            return historico_consultas[i]
    raise HTTPException(status_code=404, detail="Item não encontrado")

@app.delete("/historico/{item_id}")
def deletar_item(item_id: int):
    global historico_consultas
    historico_consultas = [item for item in historico_consultas if item["id"] != item_id]
    return {"mensagem": f"Item com ID {item_id} deletado com sucesso"}

@app.get("/grafico")
def grafico(tipo: str = Query(...), codigo: str = Query(...)):
    codigo = codigo.upper()
    if tipo == "acao":
        if not codigo.endswith(".SA") and not codigo.isalpha():
            codigo += ".SA"
        try:
            ticker = yf.Ticker(codigo)
            hist = ticker.history(period="90d")
            if hist.empty:
                return {"erro": "Histórico não encontrado."}
            return [
                {"data": idx.strftime("%d/%m"), "preco": round(row["Close"], 2)}
                for idx, row in hist.iterrows()
            ]
        except Exception as e:
            return {"erro": f"Erro ao buscar gráfico de ação: {str(e)}"}
    elif tipo == "moeda":
        try:
            ticker = yf.Ticker(f"{codigo}=X")
            hist = ticker.history(period="90d")
            if hist.empty:
                return {"erro": "Histórico não encontrado."}
            return [
                {"data": idx.strftime("%d/%m"), "preco": round(row["Close"], 4)}
                for idx, row in hist.iterrows()
            ]
        except Exception as e:
            return {"erro": f"Erro ao buscar gráfico de moeda: {str(e)}"}
    else:
        return {"erro": "Tipo inválido para gráfico. Use 'acao' ou 'moeda'."}




















