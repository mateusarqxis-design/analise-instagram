"""
Ponto de entrada principal — executa todas as análises disponíveis.

Uso:
  python main.py                  # roda tudo
  python main.py --posts          # só posts
  python main.py --stories        # só stories
  python main.py --seguidores     # só seguidores
  python main.py --amostra        # gera dados de amostra e roda tudo
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))


def main():
    parser = argparse.ArgumentParser(description="Análise de dados do Instagram")
    parser.add_argument("--posts", action="store_true", help="Analisar posts")
    parser.add_argument("--stories", action="store_true", help="Analisar stories")
    parser.add_argument("--seguidores", action="store_true", help="Analisar seguidores")
    parser.add_argument("--amostra", action="store_true", help="Gerar dados de amostra antes de analisar")
    args = parser.parse_args()

    rodar_tudo = not (args.posts or args.stories or args.seguidores)

    if args.amostra:
        from gerar_amostra import gerar_posts, gerar_stories, gerar_seguidores
        print(">>> Gerando dados de amostra...\n")
        gerar_posts()
        gerar_stories()
        gerar_seguidores()
        print()

    if args.posts or rodar_tudo:
        print(">>> Analisando posts...\n")
        try:
            from analise_posts import analisar_posts
            analisar_posts()
        except FileNotFoundError as e:
            print(f"[PULADO] {e}")
        print()

    if args.stories or rodar_tudo:
        print(">>> Analisando stories...\n")
        try:
            from analise_stories import analisar_stories
            analisar_stories()
        except FileNotFoundError as e:
            print(f"[PULADO] {e}")
        print()

    if args.seguidores or rodar_tudo:
        print(">>> Analisando seguidores...\n")
        try:
            from analise_seguidores import analisar_seguidores
            analisar_seguidores()
        except FileNotFoundError as e:
            print(f"[PULADO] {e}")
        print()

    print("=" * 50)
    print("  Análise concluída!")
    print("  Resultados em: saida/graficos/  e  saida/relatorios/")
    print("=" * 50)


if __name__ == "__main__":
    main()
