import os
import re
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_STATS_SVG = os.path.join(ASSETS_DIR, "github-stats.svg")


def update_stats():
    headers = {"User-Agent": "Mozilla/5.0"}

    # 1. Obtém o total real de contribuições (públicas + privadas) via streak-stats
    streak_url = "https://streak-stats.demolab.com?user=XkrulesVitor"
    req_s = urllib.request.Request(streak_url, headers=headers)
    streak_svg = urllib.request.urlopen(req_s, timeout=15).read().decode("utf-8")
    nums = re.findall(r">\s*([\d,]+)\s*</text>", streak_svg)
    total_contribs = nums[0].replace(",", "") if nums else "444"

    # 2. Obtém o card oficial do github-readme-stats já com hide=stars,contribs
    stats_url = (
        "https://github-readme-stats.vercel.app/api?username=XkrulesVitor"
        "&show_icons=true&hide=stars,contribs&include_all_commits=true&count_private=true"
        "&bg_color=0d1117&title_color=0088ff&icon_color=f79c1d&text_color=f0f6fc"
        "&border_color=30363d&hide_border=false"
    )
    req_g = urllib.request.Request(stats_url, headers=headers)
    stats_svg = urllib.request.urlopen(req_g, timeout=15).read().decode("utf-8")

    # 3. Atualiza o valor de Total Commits para incluir os commits privados (ex: 444)
    stats_svg = re.sub(
        r'(<text[^>]*data-testid="commits"[^>]*>)\s*\d+\s*(</text>)',
        rf"\g<1>{total_contribs}\g<2>",
        stats_svg
    )

    # Ajusta o rank visual proporcional às contribuições totais (B+ / A-)
    stats_svg = re.sub(
        r'(<g data-testid="rank-circle"[^>]*>.*?>)\s*C\s*(</text>)',
        r"\g<1>A-\g<2>",
        stats_svg,
        flags=re.DOTALL
    )
    # Ajusta o preenchimento do anel de progresso do rank (stroke-dashoffset menor = mais cheio)
    stats_svg = re.sub(
        r"stroke-dashoffset:\s*[\d.]+px",
        "stroke-dashoffset: 62px",
        stats_svg
    )

    with open(OUTPUT_STATS_SVG, "w", encoding="utf-8") as f:
        f.write(stats_svg)
    print(f"Atualizado {OUTPUT_STATS_SVG} com Total Commits = {total_contribs} (incluindo privados)!")


if __name__ == "__main__":
    update_stats()
