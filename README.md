Automador e Analisador de Invoices (PDF para JSON & Pandas)

Este projeto consiste em uma automação ponta a ponta desenvolvida em Python para otimizar o processamento de faturas comerciais (invoices). O sistema realiza a varredura dinâmica de uma pasta local, extrai metadados e tabelas de itens diretamente do texto de arquivos PDF, valida a integridade dos dados usando regras de negócio estritas e consolida tudo em uma base de dados JSON estruturada.

Na ponta final, o script utiliza a biblioteca Pandas para ler a base histórica e gerar um relatório gerencial com insights estatísticos automatizados.

Tecnologias e Bibliotecas Utilizadas

Python 3 (Linguagem base)
`pdfplumber`**: Extração cirúrgica de texto corrido diretamente das páginas dos PDFs.
`re` (Regular Expressions)**: Padrões Regex para capturar IDs textuais, datas e delimitar o mapeamento das linhas de produtos.
`Pydantic` (`BaseModel`, `Field`)**: Validação de integridade, sanidade de dados (regras comerciais como `quantidade >= 1` e `preco > 0`) e conversão automática de tipos.
`Pandas`**: Normalização de JSON aninhado (`json_normalize`), agrupamento de dados (`groupby`) e geração de métricas analíticas.
`json` & `os`**: Manipulação do sistema de arquivos e persistência de dados.

Funcionalidades Principais

1.  Varredura Dinâmica de Diretórios: Localiza e processa automaticamente todos os arquivos com a extensão `.pdf` contidos na pasta alvo.
2.  Mecanismo de Extração Híbrido: Captura dados do cabeçalho (*Order ID*, *Order Date*, *Customer ID*) e itera sobre o corpo do texto via Regex para isolar registros de produtos.
3.  Segurança e Antiduplicidade: Filtra linhas indesejadas (como totais ou rodapés) e utiliza estruturas em `set()` para impedir a inserção de produtos duplicados de uma mesma nota.
4.  Camada de Confiabilidade de Dados: Garante através do Pydantic que nenhuma string corrompida entre nos campos numéricos, lançando logs amigáveis (`ValidationError`) sem derrubar a execução do script principal.
5.  Motor Analítico Automatizado: Agrupa o histórico geral e responde na tela indicadores comerciais críticos.

Métricas Geradas no Relatório Geral

Após consolidar as notas fiscais em um arquivo estruturado, o módulo analítico exibe:
Média do valor total faturado entre todas as notas fiscais processadas.
Produto campeão em volume, indicando o item mais vendido por soma acumulada de unidades.
Faturamento total por produto, somando os valores financeiros gerados individualmente por cada SKU.
Catálogo unificado de preços, listando de forma exclusiva o nome e o preço unitário de cada produto comercializado.

Como Executar o Projeto

1. Pré-requisitos
Certifique-se de ter o Python instalado e as dependências do projeto configuradas no seu ambiente:

pip install pdfplumber 
pip install pydantic 
pip install pandas

bash
pip install pdfplumber pydantic pandas.
