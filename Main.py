import pdfplumber 
import re
from pydantic import BaseModel, Field, ValidationError
import json
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog


class Item_Pedido(BaseModel):
        id_produto: int = Field(gt=0)
        product_name: str
        quantidade: int = Field(default=1, ge=1)
        preco_unitario: float = Field(gt=0.0)

def extracao_dos_dados(caminho_pdf):
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_extraido = pdf.pages[0].extract_text()

        if not texto_extraido:
            return
        print(texto_extraido)
        order_ID = re.search(r'Order ID: \s*(\d+)', texto_extraido)
        order_Date = re.search(r'Order Date: \s*(.*)', texto_extraido)
        customer_ID = re.search(r'Customer ID: \s*(\w+)', texto_extraido)
        
        order_ID_Final = order_ID.group(1).strip() if order_ID else None
        order_Data_Final = order_Date.group(1).strip() if order_Date else None
        customer_ID_Final = customer_ID.group(1).strip() if customer_ID else None
        
        lista_produtos_validados = []
        ids_adicionados = set()
        padrao_linha = re.compile(r'^(\d+)\s+(.+?)\s+(\d+)\s+(\d+\.\d+|\d+)')
        
        for linha_texto in texto_extraido.split("\n"):
            resultado = padrao_linha.match(linha_texto.strip())
            
            if resultado:
                try:
                    item = Item_Pedido(
                        id_produto=resultado.group(1),
                        product_name=resultado.group(2),
                        quantidade=resultado.group(3),
                        preco_unitario=resultado.group(4)
                    )
                    if item.id_produto not in ids_adicionados:
                        lista_produtos_validados.append(item)
                        ids_adicionados.add(item.id_produto)
                except ValidationError as e:
                    print(f"Linha ignorada devido ao erro de validação: {e}")
        return{
            "order_id": order_ID_Final,
            "order_date": order_Data_Final,
            "customer_id": customer_ID_Final,
            "items": [prod.model_dump() for prod in lista_produtos_validados]   
        }
    except Exception as e:
        print(f"Erro ao processar o arquivo {caminho_pdf}: {e}")
        return None    
    
def processar_pasta_de_pdfs(caminho_da_pasta):
    todas_as_notas = []

    arquivos = os.listdir(caminho_da_pasta)

    for arquivo in arquivos:
        if arquivo.lower().endswith('.pdf'):
            caminho_completo = os.path.join(caminho_da_pasta, arquivo)

            dados_nota = extracao_dos_dados(caminho_completo)

            if dados_nota:
                todas_as_notas.append(dados_nota)

    return todas_as_notas

def analisar_dados_invoice(arquivo_json):
    try:
        with open(arquivo_json, "r", encoding="utf-8") as f:
            dados_json = json.load(f)

        if not dados_json:
            print("Arquivo vazio")
            return
        
        df_itens = pd.json_normalize(
            dados_json,
            record_path=["items"],
            meta=["order_id", "order_date", "customer_id"]
        )
        
        #Multiplicando a quantidade pelo preço do item
        df_itens["valor_total_item"] = df_itens["quantidade"] * df_itens["preco_unitario"].sum()

        total_invoice = df_itens.groupby("order_id")["valor_total_item"].sum()
        media_invoice = total_invoice.mean()
        print(f"\n1. A média total dos invoices é: {media_invoice: .2f}")

        volume_produtos = df_itens.groupby("product_name")["quantidade"].sum()
        produto_mais_vendido = volume_produtos.idxmax()
        qtd_total_unidades = volume_produtos.max()
        
        print(f"\n2. Produto mais vendido (em quantidade de unidades): {produto_mais_vendido} com o total de {qtd_total_unidades} unidades vendidas")

        total_gasto_por_produto = df_itens.groupby("product_name")["valor_total_item"].sum().reset_index()
        print("\n3. Valor total gasto por cada produto:")
        print(total_gasto_por_produto.to_string(index=False, formatters={"valor_total_item": "R$ {:.2f}".format}))

        produtos_unicos = df_itens[["product_name", "preco_unitario"]].drop_duplicates().reset_index(drop=True)
        print("\n4. Listagem de produtos: ")
        print(produtos_unicos.to_string(index=False, formatters={"preco_unitario": "R$ {:.2f}".format}))
        print("\n" + "="*40)

    except FileNotFoundError:
        print(f"[Erro] O arquivo '{arquivo_json}' não foi encontrado.")
    except Exception as e:
        print(f"[Erro] Ocorreu uma falha ao analisar os dados: {e}")

root = tk.Tk()
root.withdraw()
caminho_pasta = filedialog.askdirectory(title="Selecione a pasta dos PDFs das Invoices")

resultado_final = processar_pasta_de_pdfs(caminho_pasta)
analisar_dados_invoice(arquivo_json="database.json")
