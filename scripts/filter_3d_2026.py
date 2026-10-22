import datetime
import glob
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRIB_DIR = os.path.join(BASE_DIR, "profile-3d-contrib")


def process_svg_file(svg_path):
    with open(svg_path, "r", encoding="utf-8") as f:
        s = f.read()

    # 1. Localiza o intervalo de datas original (ex: 2025-10-19 / 2026-10-22)
    m_date = re.search(r"(\d{4}-\d{2}-\d{2})\s*/\s*(\d{4}-\d{2}-\d{2})", s)
    if not m_date:
        return

    start_str, end_str = m_date.group(1), m_date.group(2)
    start_date = datetime.date.fromisoformat(start_str)
    target_start = datetime.date(2026, 1, 1)

    # Se o gráfico original começa em 2025, filtramos as semanas de 2025 do tabuleiro 3D
    if start_date < target_start:
        board_match = re.search(
            r'(<rect x="0" y="0" width="1280" height="850"[^>]*></rect><g>)(.*?</g>)(</g><g transform="translate\()',
            s,
            flags=re.DOTALL
        )
        if board_match:
            prefix, cells_html, suffix = board_match.groups()
            cell_pattern = re.compile(r'<g transform="translate\(([\d.]+) ([\d.]+)\)">.*?</g>', re.DOTALL)
            cells = list(cell_pattern.finditer(cells_html))

            days_diff = (target_start - start_date).days
            weeks_to_skip = days_diff // 7  # 10 semanas completas de 2025

            kept_cells = []
            for idx, m in enumerate(cells):
                cell_date = start_date + datetime.timedelta(days=idx)
                week_idx = idx // 7
                if week_idx < weeks_to_skip:
                    continue
                cell_str = m.group(0)
                if cell_date < target_start and "animateTransform" in cell_str:
                    x_val, y_val = m.group(1), m.group(2)
                    anim_m = re.search(r'values="[\d.]+ ([\d.]+);', cell_str)
                    base_y = anim_m.group(1) if anim_m else y_val
                    cell_str = re.sub(r'<animateTransform.*?</animateTransform>', '', cell_str)
                    cell_str = re.sub(r'transform="translate\([\d.]+ [\d.]+\)"', f'transform="translate({x_val} {base_y})"', cell_str)
                    cell_str = re.sub(r'-l[1-4]-', '-l0-', cell_str)
                    cell_str = re.sub(r'height="[\d.]+"(\s+transform="(?:skewY\(30\)|translate\(18 10\.39\)))', r'height="2.6"\1', cell_str)
                    cell_str = re.sub(r'<animate attributeName="height".*?</animate>', '', cell_str)
                kept_cells.append(cell_str)

            shift_x = -weeks_to_skip * 10.0
            shift_y = -weeks_to_skip * 5.77
            new_board = f'{prefix}<g transform="translate({shift_x:.1f} {shift_y:.2f})">' + "".join(kept_cells) + "</g>" + suffix
            s = s[:board_match.start()] + new_board + s[board_match.end():]

        s = re.sub(
            r"\d{4}-\d{2}-\d{2}\s*/\s*\d{4}-\d{2}-\d{2}",
            f"2026-01-01 / {end_str}",
            s
        )

    # 2. Remove os contadores de estrelas (stars) e forks do rodapé do gráfico 3D
    s = re.sub(
        r'<g transform="translate\(608,\s*802\),\s*scale\(2\)">.*?</text><g transform="translate\(736,\s*802\),\s*scale\(2\)">.*?</text>',
        "",
        s,
        flags=re.DOTALL
    )

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(s)


def main():
    svg_files = glob.glob(os.path.join(CONTRIB_DIR, "*.svg"))
    for p in svg_files:
        process_svg_file(p)
    print(f"Filtrados {len(svg_files)} arquivos SVG 3D para iniciar em 2026-01-01 (sem stars/forks)!")


if __name__ == "__main__":
    main()
