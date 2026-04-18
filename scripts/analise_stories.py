"""
Análise de Stories do Instagram.

Colunas esperadas no CSV:
  Timestamp, Impressions, Reach, Replies, Exits, Taps_Forward,
  Taps_Back, Link_Clicks
"""

import pandas as pd
import matplotlib.pyplot as plt
from utils import carregar_csv, salvar_csv, salvar_relatorio, resumo_dataframe, PASTA_GRAFICOS


def analisar_stories(nome_csv: str = "stories.csv"):
    df = carregar_csv(nome_csv)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["hora"] = df["timestamp"].dt.hour
        df["dia_semana"] = df["timestamp"].dt.day_name()

    resumo_dataframe(df, "STORIES")

    metricas = [c for c in ["impressions", "reach", "replies", "exits", "taps_forward", "taps_back"] if c in df.columns]

    # --- Taxa de retenção ---
    if {"impressions", "exits"}.issubset(df.columns):
        df["retencao"] = ((df["impressions"] - df["exits"]) / df["impressions"] * 100).round(2)
        media_retencao = df["retencao"].mean().round(2)
    else:
        media_retencao = "N/A"

    # --- Relatório ---
    stats = df[metricas].describe().round(2) if metricas else "N/A"
    relatorio = f"""RELATÓRIO — ANÁLISE DE STORIES
{'='*50}

Total de stories analisados: {len(df):,}
Taxa de retenção média     : {media_retencao}%

ESTATÍSTICAS POR MÉTRICA:
{stats.to_string() if isinstance(stats, pd.DataFrame) else stats}
"""
    salvar_relatorio(relatorio, "relatorio_stories.txt")
    salvar_csv(df, "stories_processados.csv")

    # --- Gráficos ---
    PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)

    if metricas:
        fig, ax = plt.subplots(figsize=(10, 4))
        df[metricas].mean().sort_values().plot(kind="barh", ax=ax, color="#833AB4", edgecolor="white")
        ax.set_title("Média das Métricas de Stories")
        ax.set_xlabel("Valor médio")
        plt.tight_layout()
        plt.savefig(PASTA_GRAFICOS / "stories_metricas.png", dpi=150)
        plt.close()
        print("[OK] Gráfico salvo: stories_metricas.png")

    print("\n[CONCLUIDO] Análise de stories finalizada.")
    return df


if __name__ == "__main__":
    analisar_stories()
