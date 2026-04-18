"""
Análise de seguidores e seguindo do Instagram.

Colunas esperadas:
  seguidores.csv  -> Username, Full_Name, Followed_At
  seguindo.csv    -> Username, Full_Name, Following_Since
"""

import pandas as pd
import matplotlib.pyplot as plt
from utils import carregar_csv, salvar_csv, salvar_relatorio, resumo_dataframe, PASTA_GRAFICOS


def analisar_seguidores(
    csv_seguidores: str = "seguidores.csv",
    csv_seguindo: str = "seguindo.csv",
):
    resultados = {}

    # --- Seguidores ---
    try:
        seg = carregar_csv(csv_seguidores)
        seg.columns = [c.strip().lower().replace(" ", "_") for c in seg.columns]
        resumo_dataframe(seg, "SEGUIDORES")

        if "followed_at" in seg.columns:
            seg["followed_at"] = pd.to_datetime(seg["followed_at"], errors="coerce")
            novos_por_mes = seg.groupby(seg["followed_at"].dt.to_period("M")).size()
        else:
            novos_por_mes = None

        resultados["seguidores"] = seg
    except FileNotFoundError:
        print("[AVISO] seguidores.csv não encontrado — pulando.")
        seg = None
        novos_por_mes = None

    # --- Seguindo ---
    try:
        snd = carregar_csv(csv_seguindo)
        snd.columns = [c.strip().lower().replace(" ", "_") for c in snd.columns]
        resumo_dataframe(snd, "SEGUINDO")
        resultados["seguindo"] = snd
    except FileNotFoundError:
        print("[AVISO] seguindo.csv não encontrado — pulando.")
        snd = None

    # --- Análise cruzada ---
    nao_seguem_de_volta = []
    voce_nao_segue_de_volta = []

    if seg is not None and snd is not None and "username" in seg.columns and "username" in snd.columns:
        set_seg = set(seg["username"].dropna().str.lower())
        set_snd = set(snd["username"].dropna().str.lower())
        nao_seguem_de_volta = sorted(set_snd - set_seg)
        voce_nao_segue_de_volta = sorted(set_seg - set_snd)

    # --- Relatório ---
    relatorio = f"""RELATÓRIO — ANÁLISE DE SEGUIDORES
{'='*50}

Total de seguidores : {len(seg) if seg is not None else 'N/A':,}
Total seguindo      : {len(snd) if snd is not None else 'N/A':,}

Você segue mas eles NÃO te seguem de volta ({len(nao_seguem_de_volta)}):
{chr(10).join(f'  - {u}' for u in nao_seguem_de_volta[:50])}
{'  ... (lista completa em nao_seguem_de_volta.csv)' if len(nao_seguem_de_volta) > 50 else ''}

Te seguem mas você NÃO segue de volta ({len(voce_nao_segue_de_volta)}):
{chr(10).join(f'  - {u}' for u in voce_nao_segue_de_volta[:50])}
{'  ... (lista completa em voce_nao_segue_de_volta.csv)' if len(voce_nao_segue_de_volta) > 50 else ''}
"""
    salvar_relatorio(relatorio, "relatorio_seguidores.txt")

    if nao_seguem_de_volta:
        salvar_csv(pd.DataFrame({"username": nao_seguem_de_volta}), "nao_seguem_de_volta.csv")
    if voce_nao_segue_de_volta:
        salvar_csv(pd.DataFrame({"username": voce_nao_segue_de_volta}), "voce_nao_segue_de_volta.csv")

    # --- Gráfico: crescimento de seguidores ---
    if novos_por_mes is not None and len(novos_por_mes) > 1:
        PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)
        fig, ax = plt.subplots(figsize=(12, 4))
        novos_por_mes.plot(ax=ax, kind="bar", color="#E1306C", edgecolor="white")
        ax.set_title("Novos Seguidores por Mês")
        ax.set_xlabel("Mês")
        ax.set_ylabel("Quantidade")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(PASTA_GRAFICOS / "crescimento_seguidores.png", dpi=150)
        plt.close()
        print("[OK] Gráfico salvo: crescimento_seguidores.png")

    print("\n[CONCLUIDO] Análise de seguidores finalizada.")
    return resultados


if __name__ == "__main__":
    analisar_seguidores()
