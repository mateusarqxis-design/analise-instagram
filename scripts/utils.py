"""
Utilitários compartilhados para análise de dados do Instagram.
"""

import pandas as pd
from pathlib import Path

PASTA_BRUTOS = Path(__file__).parent.parent / "dados" / "brutos"
PASTA_PROCESSADOS = Path(__file__).parent.parent / "dados" / "processados"
PASTA_GRAFICOS = Path(__file__).parent.parent / "saida" / "graficos"
PASTA_RELATORIOS = Path(__file__).parent.parent / "saida" / "relatorios"


def carregar_csv(nome_arquivo: str, **kwargs) -> pd.DataFrame:
    """Carrega um CSV da pasta de dados brutos."""
    caminho = PASTA_BRUTOS / nome_arquivo
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    df = pd.read_csv(caminho, **kwargs)
    print(f"[OK] {nome_arquivo} carregado — {len(df)} linhas, {len(df.columns)} colunas")
    return df


def salvar_csv(df: pd.DataFrame, nome_arquivo: str):
    """Salva um DataFrame na pasta de dados processados."""
    PASTA_PROCESSADOS.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_PROCESSADOS / nome_arquivo
    df.to_csv(caminho, index=False)
    print(f"[OK] Salvo em: {caminho}")


def salvar_relatorio(conteudo: str, nome_arquivo: str):
    """Salva um relatório em texto na pasta de saída."""
    PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_RELATORIOS / nome_arquivo
    caminho.write_text(conteudo, encoding="utf-8")
    print(f"[OK] Relatório salvo em: {caminho}")


def resumo_dataframe(df: pd.DataFrame, titulo: str = ""):
    """Imprime um resumo básico do DataFrame."""
    print(f"\n{'='*50}")
    if titulo:
        print(f"  {titulo}")
        print(f"{'='*50}")
    print(f"  Linhas     : {len(df):,}")
    print(f"  Colunas    : {list(df.columns)}")
    print(f"  Nulos      : {df.isnull().sum().to_dict()}")
    print(f"{'='*50}\n")
