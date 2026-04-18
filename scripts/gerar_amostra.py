"""
Gera CSVs de amostra para testar a análise sem dados reais.
Execute: python gerar_amostra.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import random

PASTA_BRUTOS = Path(__file__).parent.parent / "dados" / "brutos"
PASTA_BRUTOS.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)


def gerar_posts(n: int = 120):
    datas = [datetime(2024, 1, 1) + timedelta(days=int(d)) for d in rng.integers(0, 365, n)]
    datas.sort()
    tipos = rng.choice(["IMAGE", "VIDEO", "CAROUSEL"], n, p=[0.6, 0.2, 0.2])
    df = pd.DataFrame({
        "Timestamp": [d.strftime("%Y-%m-%d %H:%M:%S") for d in datas],
        "Caption": [f"Post #{i+1} - legenda de exemplo." for i in range(n)],
        "Likes": rng.integers(50, 2000, n),
        "Comments": rng.integers(1, 150, n),
        "Impressions": rng.integers(500, 15000, n),
        "Reach": rng.integers(400, 12000, n),
        "Saves": rng.integers(5, 500, n),
        "Shares": rng.integers(0, 200, n),
        "Media_Type": tipos,
    })
    caminho = PASTA_BRUTOS / "posts.csv"
    df.to_csv(caminho, index=False)
    print(f"[OK] posts.csv gerado ({n} linhas) → {caminho}")


def gerar_stories(n: int = 200):
    datas = [datetime(2024, 1, 1) + timedelta(days=int(d), hours=int(h))
             for d, h in zip(rng.integers(0, 365, n), rng.integers(8, 22, n))]
    imp = rng.integers(100, 5000, n)
    exits = rng.integers(10, imp)
    df = pd.DataFrame({
        "Timestamp": [d.strftime("%Y-%m-%d %H:%M:%S") for d in datas],
        "Impressions": imp,
        "Reach": (imp * rng.uniform(0.7, 1.0, n)).astype(int),
        "Replies": rng.integers(0, 30, n),
        "Exits": exits,
        "Taps_Forward": rng.integers(5, 200, n),
        "Taps_Back": rng.integers(0, 50, n),
        "Link_Clicks": rng.integers(0, 40, n),
    })
    caminho = PASTA_BRUTOS / "stories.csv"
    df.to_csv(caminho, index=False)
    print(f"[OK] stories.csv gerado ({n} linhas) → {caminho}")


def gerar_seguidores(n_seg: int = 1500, n_snd: int = 800):
    nomes = [f"usuario_{i:04d}" for i in range(max(n_seg, n_snd) + 200)]
    seg_users = random.sample(nomes, n_seg)
    snd_users = random.sample(nomes, n_snd)

    datas_seg = [datetime(2020, 1, 1) + timedelta(days=int(d)) for d in rng.integers(0, 1500, n_seg)]
    pd.DataFrame({
        "Username": seg_users,
        "Full_Name": [u.replace("_", " ").title() for u in seg_users],
        "Followed_At": [d.strftime("%Y-%m-%d") for d in datas_seg],
    }).to_csv(PASTA_BRUTOS / "seguidores.csv", index=False)
    print(f"[OK] seguidores.csv gerado ({n_seg} linhas)")

    datas_snd = [datetime(2020, 1, 1) + timedelta(days=int(d)) for d in rng.integers(0, 1500, n_snd)]
    pd.DataFrame({
        "Username": snd_users,
        "Full_Name": [u.replace("_", " ").title() for u in snd_users],
        "Following_Since": [d.strftime("%Y-%m-%d") for d in datas_snd],
    }).to_csv(PASTA_BRUTOS / "seguindo.csv", index=False)
    print(f"[OK] seguindo.csv gerado ({n_snd} linhas)")


if __name__ == "__main__":
    print("Gerando dados de amostra...\n")
    gerar_posts()
    gerar_stories()
    gerar_seguidores()
    print("\n[PRONTO] Dados de amostra salvos em dados/brutos/")
