import io
import os
import re
import urllib.request
import resvg_py
from PIL import Image, ImageDraw, ImageOps

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_PNG = os.path.join(ASSETS_DIR, "tech-stack.png")

# 18 ícones nativos do skillicons.dev (sem firebase, pois usaremos o Firebase_icon.svg limpo)
SKILLICONS_KEYS = [
    "html", "css", "js", "ts", "react", "nextjs",
    "c", "cpp", "java", "py", "blender", "figma",
    "supabase", "postgres", "mysql", "git", "github", "vscode"
]


def make_rounded_mask(size=256, radius=60):
    """Cria máscara anti-aliased (4x supersampled) de quadrado arredondado."""
    scale = 4
    big = Image.new("L", (size * scale, size * scale), 0)
    draw = ImageDraw.Draw(big)
    draw.rounded_rectangle((0, 0, size * scale - 1, size * scale - 1), radius=radius * scale, fill=255)
    return big.resize((size, size), Image.Resampling.LANCZOS)


def make_dark_tile_base(size=256, radius=60, color=(36, 41, 56, 255)):
    """Cria um bloco base dark (#242938) no padrão exato do Skill Icons."""
    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = make_rounded_mask(size, radius)
    bg = Image.new("RGBA", (size, size), color)
    tile.paste(bg, (0, 0), mask)
    return tile


def fetch_single_skillicon_png(key):
    """Baixa e renderiza individualmente cada ícone do skillicons.dev sem risco de colisão de IDs."""
    url = f"https://skillicons.dev/icons?i={key}&theme=dark"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        svg_text = r.read().decode("utf-8")
    png_bytes = resvg_py.svg_to_bytes(svg_text, width=256, height=256)
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def build_construct3_tile():
    tile = make_dark_tile_base()
    svg_path = os.path.join(ASSETS_DIR, "Construct_3_Logo.svg")
    with open(svg_path, "r", encoding="utf-8") as f:
        svg_text = f.read()
    png_bytes = resvg_py.svg_to_bytes(svg_text, width=184, height=184)
    logo = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    tile.alpha_composite(logo, ((256 - 184) // 2, (256 - 184) // 2))
    return tile


def build_gamemaker_tile():
    """Ícone oficial do GameMaker extraído do GameMaker-LTS2026.exe (losango branco sobre fundo escuro)."""
    tile = make_dark_tile_base()
    gm_path = os.path.join(ASSETS_DIR, "gm_exe_9.png")
    im = Image.open(gm_path).convert("RGBA")
    # O ícone original tem linhas pretas com preenchimento branco; no tema escuro deixamos o símbolo todo branco nítido
    r, g, b, a = im.split()
    white_logo = Image.new("RGBA", im.size, (255, 255, 255, 255))
    white_logo.putalpha(a)
    white_logo = white_logo.resize((184, 184), Image.Resampling.LANCZOS)
    tile.alpha_composite(white_logo, ((256 - 184) // 2, (256 - 184) // 2))
    return tile


def build_gml_tile():
    """Ícone oficial do GML (GameMaker Language - chaves verdes da YoYo Games)."""
    tile = make_dark_tile_base()
    gml_path = os.path.join(ASSETS_DIR, "Gamemaker_language.png")
    im = Image.open(gml_path).convert("RGBA")
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    scale = min(184 / w, 184 / h)
    nw, nh = int(w * scale), int(h * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    tile.alpha_composite(im, ((256 - nw) // 2, (256 - nh) // 2))
    return tile


def build_firebase_tile():
    """Novo ícone oficial multi-colorido do Firebase (extraído de New_Firebase_logo.svg)."""
    tile = make_dark_tile_base()
    fb_path = os.path.join(ASSETS_DIR, "New_Firebase_logo.svg")
    with open(fb_path, "r", encoding="utf-8") as f:
        svg_text = f.read()
    png_bytes = resvg_py.svg_to_bytes(svg_text, width=749 * 2, height=205 * 2)
    full_img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    # Recorta apenas o símbolo da chama à esquerda (x: 0..350)
    flame = full_img.crop((0, 0, 350, full_img.size[1]))
    bbox = flame.getbbox()
    if bbox:
        flame = flame.crop(bbox)
    w, h = flame.size
    scale = min(184 / w, 184 / h)
    nw, nh = int(w * scale), int(h * scale)
    flame = flame.resize((nw, nh), Image.Resampling.LANCZOS)
    tile.alpha_composite(flame, ((256 - nw) // 2, (256 - nh) // 2))
    return tile


def build_antigravity_tile():
    """Logo oficial do Antigravity enviada pelo usuário (removendo o fundo branco suavemente)."""
    tile = make_dark_tile_base()
    agy_path = os.path.join(ASSETS_DIR, "logo_antigravity.png")
    im = Image.open(agy_path).convert("RGBA")
    pixels = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            # Calcula distância para o branco puro (255, 255, 255)
            dist = max(255 - r, 255 - g, 255 - b)
            if dist < 12:
                pixels[x, y] = (r, g, b, 0)
            elif dist < 45:
                alpha = int(255 * (dist - 12) / 33.0)
                pixels[x, y] = (r, g, b, min(a, alpha))

    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    bw, bh = im.size
    scale = min(176 / bw, 176 / bh)
    nw, nh = int(bw * scale), int(bh * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    tile.alpha_composite(im, ((256 - nw) // 2, (256 - nh) // 2))
    return tile


def build_codex_tile():
    """Logo oficial do Codex enviada pelo usuário."""
    tile = make_dark_tile_base()
    codex_path = os.path.join(ASSETS_DIR, "logo_codex.png")
    im = Image.open(codex_path).convert("RGBA")
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    bw, bh = im.size
    scale = min(192 / bw, 192 / bh)
    nw, nh = int(bw * scale), int(bh * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    tile.alpha_composite(im, ((256 - nw) // 2, (256 - nh) // 2))
    return tile


def build_claude_tile():
    """Logo oficial do Claude enviada pelo usuário com cantos arredondados padrão rx=60."""
    claude_path = os.path.join(ASSETS_DIR, "logo_claude.jpg")
    im = Image.open(claude_path).convert("RGBA").resize((256, 256), Image.Resampling.LANCZOS)
    mask = make_rounded_mask(256, 60)
    tile = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    tile.paste(im, (0, 0), mask)
    return tile


def main():
    print("Baixando e renderizando ícones individuais...")
    tiles = {}
    for k in SKILLICONS_KEYS:
        tiles[k] = fetch_single_skillicon_png(k)

    tiles["construct3"] = build_construct3_tile()
    tiles["gamemaker"] = build_gamemaker_tile()
    tiles["gml"] = build_gml_tile()
    tiles["firebase"] = build_firebase_tile()
    tiles["antigravity"] = build_antigravity_tile()
    tiles["codex"] = build_codex_tile()
    tiles["claude"] = build_claude_tile()

    # Ordem das 25 tecnologias e ferramentas em um único bloco (13 na linha 1 + 12 centralizados na linha 2)
    row1 = ["html", "css", "js", "ts", "react", "nextjs", "c", "cpp", "java", "py", "construct3", "gamemaker", "gml"]
    row2 = ["blender", "figma", "supabase", "firebase", "postgres", "mysql", "git", "github", "vscode", "antigravity", "codex", "claude"]

    tile_size = 112
    gap = 18
    cols_max = len(row1)
    canvas_w = cols_max * tile_size + (cols_max - 1) * gap
    canvas_h = 2 * tile_size + gap

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

    # Renderiza Linha 1 (13 ícones)
    for i, key in enumerate(row1):
        t_img = tiles[key].resize((tile_size, tile_size), Image.Resampling.LANCZOS)
        x = i * (tile_size + gap)
        canvas.alpha_composite(t_img, (x, 0))

    # Renderiza Linha 2 (12 ícones, perfeitamente centralizados em relação à linha 1)
    row2_w = len(row2) * tile_size + (len(row2) - 1) * gap
    offset_x = (canvas_w - row2_w) // 2
    for i, key in enumerate(row2):
        t_img = tiles[key].resize((tile_size, tile_size), Image.Resampling.LANCZOS)
        x = offset_x + i * (tile_size + gap)
        y = tile_size + gap
        canvas.alpha_composite(t_img, (x, y))

    canvas.save(OUTPUT_PNG, "PNG")
    print(f"Salvo {OUTPUT_PNG} ({canvas.size[0]}x{canvas.size[1]}) com todas as 25 tecnologias!")


if __name__ == "__main__":
    main()
