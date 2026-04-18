"""
Análise de posts do Instagram.

Colunas esperadas no CSV:
  Timestamp, Caption, Likes, Comments, Impressions, Reach,
  Saves, Shares, Profile_Visits, Follows, Media_Type
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from utils import carregar_csv, salvar_csv, salvar_relatorio, resumo_dataframe, PASTA_GRAFICOS


def analisar_posts(nome_csv: str = "posts.csv"):
    df = carregar_csv(nome_csv)

    # --- Normalização de colunas ---
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["ano"] = df["timestamp"].dt.year
        df["mes"] = df["timestamp"].dt.month
        df["dia_semana"] = df["timestamp"].dt.day_name()
        df["hora"] = df["timestamp"].dt.hour

    resumo_dataframe(df, "POSTS")

    metricas_num = [c for c in ["likes", "comments", "impressions", "reach", "saves", "shares"] if c in df.columns]

    # --- Estatísticas gerais ---
    stats = df[metricas_num].describe().round(2)

    # --- Melhor horário para postar ---
    if "hora" in df.columns and "likes" in df.columns:
        por_hora = df.groupby("hora")["likes"].mean().sort_values(ascending=False)
        melhor_hora = por_hora.idxmax()
    else:
        por_hora = None
        melhor_hora = "N/A"

    # --- Melhor dia da semana ---
    if "dia_semana" in df.columns and "likes" in df.columns:
        ordem_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        por_dia = df.groupby("dia_semana")["likes"].mean().reindex(ordem_dias).dropna()
        melhor_dia = por_dia.idxmax()
    else:
        por_dia = None
        melhor_dia = "N/A"

    # --- Taxa de engajamento ---
    if {"likes", "comments", "reach"}.issubset(df.columns):
        df["engajamento"] = ((df["likes"] + df["comments"]) / df["reach"] * 100).round(2)
        media_eng = df["engajamento"].mean().round(2)
    else:
        media_eng = "N/A"

    # --- Relatório de texto ---
    relatorio = f"""RELATÓRIO — ANÁLISE DE POSTS
{'='*50}

Total de posts analisados : {len(df):,}
Taxa de engajamento média : {media_eng}%
Melhor horário para postar: {melhor_hora}h
Melhor dia da semana      : {melhor_dia}

ESTATÍSTICAS POR MÉTRICA:
{stats.to_string()}
"""
    salvar_relatorio(relatorio, "relatorio_posts.txt")
    salvar_csv(df, "posts_processados.csv")

    # --- Gráficos ---
    PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)

    if len(metricas_num) > 0:
        fig, axes = plt.subplots(1, len(metricas_num), figsize=(5 * len(metricas_num), 4))
        if len(metricas_num) == 1:
            axes = [axes]
        for ax, col in zip(axes, metricas_num):
            df[col].dropna().hist(ax=ax, bins=20, color="#E1306C", edgecolor="white")
            ax.set_title(col.capitalize())
            ax.set_xlabel("Valor")
            ax.set_ylabel("Frequência")
        plt.suptitle("Distribuição das Métricas de Posts", fontsize=14, fontweight="bold")
        plt.tight_layout()
        plt.savefig(PASTA_GRAFICOS / "posts_distribuicao.png", dpi=150)
        plt.close()
        print("[OK] Gráfico salvo: posts_distribuicao.png")

    if por_hora is not None:
        fig, ax = plt.subplots(figsize=(10, 4))
        por_hora.sort_index().plot(kind="bar", ax=ax, color="#833AB4", edgecolor="white")
        ax.set_title("Média de Likes por Hora do Dia")
        ax.set_xlabel("Hora")
        ax.set_ylabel("Likes médios")
        plt.tight_layout()
        plt.savefig(PASTA_GRAFICOS / "posts_hora.png", dpi=150)
        plt.close()
        print("[OK] Gráfico salvo: posts_hora.png")

    if por_dia is not None:
        fig, ax = plt.subplots(figsize=(8, 4))
        por_dia.plot(kind="bar", ax=ax, color="#FCAF45", edgecolor="white")
        ax.set_title("Média de Likes por Dia da Semana")
        ax.set_xlabel("Dia")
        ax.set_ylabel("Likes médios")
        plt.tight_layout()
        plt.savefig(PASTA_GRAFICOS / "posts_dia_semana.png", dpi=150)
        plt.close()
        print("[OK] Gráfico salvo: posts_dia_semana.png")

    print("\n[CONCLUIDO] Análise de posts finalizada.")
    return df


if __name__ == "__main__":
    analisar_posts()
