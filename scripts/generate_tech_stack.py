import os
import re
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_SVG = os.path.join(BASE_DIR, "assets", "tech-stack.svg")

# 19 ícones nativos do skillicons.dev na ordem lógica:
# Web/Front -> Linguagens -> Banco/Backend -> 3D/Design -> Ferramentas
SKILLICONS_LIST = [
    "html", "css", "js", "ts", "react", "nextjs",
    "c", "cpp", "java", "py", "blender", "figma",
    "supabase", "firebase", "postgres", "mysql",
    "git", "github", "vscode"
]

def fetch_skillicons_tiles():
    url = f"https://skillicons.dev/icons?i={','.join(SKILLICONS_LIST)}&perline=19&theme=dark"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        svg_text = r.read().decode("utf-8")

    # Extrai cada bloco <svg ...>...</svg> interno de 256x256
    pattern = re.compile(r'<g transform="translate\(\d+, \d+\)">\s*(<svg.*?</svg>)\s*</g>', re.DOTALL)
    tiles = pattern.findall(svg_text)
    return dict(zip(SKILLICONS_LIST, tiles))

# Tiles extras customizados no mesmo padrão exato (256x256, rx=60, fill=#242938)
EXTRA_TILES = {
    "construct3": """<svg width="256" height="256" viewBox="0 0 256 256" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="256" height="256" rx="60" fill="#242938"/>
      <g transform="translate(38, 38) scale(7.5)">
        <path fill="#00FFDA" d="M12.392 0c-6.752 0-12 5.498-12 12 0 6.574 5.313 12 12 12 4.283 0 8.087-2.254 10.217-5.704a.571.571 0 0 0-.2-.795l-5.55-3.204a.572.572 0 0 0-.76.177 4.453 4.453 0 0 1-3.707 1.983c-2.458 0-4.458-2-4.458-4.457 0-2.458 2-4.457 4.458-4.457 1.491 0 2.877.741 3.707 1.983a.571.571 0 0 0 .76.177l5.55-3.204a.571.571 0 0 0 .2-.795A11.998 11.998 0 0 0 12.392 0zm0 3.527c3.048 0 5.72 1.61 7.213 4.026l-2.99 1.726c-.037.021-.085.013-.108-.026a4.942 4.942 0 0 0-4.115-2.2A4.953 4.953 0 0 0 7.445 12c0 .9.241 1.745.663 2.473l-2.342 1.353a.327.327 0 0 0-.112.458 7.977 7.977 0 0 0 6.738 3.7 7.978 7.978 0 0 0 6.789-3.781l2.983 1.722a.08.08 0 0 1 .028.113 11.447 11.447 0 0 1-9.8 5.472C6.045 23.51.882 18.346.882 12c0-2.095.562-4.06 1.544-5.754l2.35 1.356c.15.088.345.04.439-.11a8.467 8.467 0 0 1 7.177-3.966zM22.965 8.95a.666.666 0 0 0-.336.088l-4.149 2.395a.654.654 0 0 0 0 1.131l4.149 2.396c.434.25.98-.064.98-.566v-4.79a.655.655 0 0 0-.644-.654zm-.663 1.785v2.528L20.112 12z"/>
      </g>
    </svg>""",

    "gamemaker": """<svg width="256" height="256" viewBox="0 0 256 256" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="256" height="256" rx="60" fill="#242938"/>
      <g transform="translate(44, 28) scale(7.0)">
        <path fill="#00ECAC" d="M.012 11.994 12.006 0l11.982 12.006h-6.831l-5.163-5.151-5.151 5.151 5.163 5.151v-5.151h5.151v6.903L12.006 24z"/>
      </g>
      <rect x="68" y="198" width="120" height="36" rx="10" fill="#0d1117" stroke="#00ECAC" stroke-width="3"/>
      <text x="128" y="223" text-anchor="middle" fill="#00ECAC" font-family="Consolas, monospace" font-weight="bold" font-size="24">GML</text>
    </svg>""",

    "antigravity": """<svg width="256" height="256" viewBox="0 0 256 256" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="256" height="256" rx="60" fill="#242938"/>
      <defs>
        <linearGradient id="agyGrad" x1="36" y1="36" x2="220" y2="220" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stop-color="#38BDF8"/>
          <stop offset="50%" stop-color="#0088FF"/>
          <stop offset="100%" stop-color="#F79C1D"/>
        </linearGradient>
      </defs>
      <!-- Símbolo orbital / prisma Antigravity -->
      <ellipse cx="128" cy="134" rx="82" ry="32" transform="rotate(-24 128 134)" stroke="url(#agyGrad)" stroke-width="10" fill="none"/>
      <path d="M128 42 L192 186 L156 186 L128 120 L100 186 L64 186 Z" fill="url(#agyGrad)"/>
      <circle cx="128" cy="96" r="10" fill="#FFFFFF"/>
    </svg>""",

    "codex": """<svg width="256" height="256" viewBox="0 0 256 256" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="256" height="256" rx="60" fill="#242938"/>
      <rect x="38" y="46" width="180" height="164" rx="24" fill="#10A37F" fill-opacity="0.16" stroke="#10A37F" stroke-width="10"/>
      <path d="M78 102 L112 128 L78 154" stroke="#10A37F" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>
      <line x1="126" y1="154" x2="174" y2="154" stroke="#F0F6FC" stroke-width="14" stroke-linecap="round"/>
      <text x="128" y="194" text-anchor="middle" fill="#10A37F" font-family="Consolas, monospace" font-weight="bold" font-size="22">CODEX</text>
    </svg>""",

    "claude": """<svg width="256" height="256" viewBox="0 0 256 256" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="256" height="256" rx="60" fill="#242938"/>
      <g transform="translate(38, 38) scale(7.5)">
        <path fill="#D97757" d="m4.7144 15.9555 4.7174-2.6471.079-.2307-.079-.1275h-.2307l-.7893-.0486-2.6956-.0729-2.3375-.0971-2.2646-.1214-.5707-.1215-.5343-.7042.0546-.3522.4797-.3218.686.0608 1.5179.1032 2.2767.1578 1.6514.0972 2.4468.255h.3886l.0546-.1579-.1336-.0971-.1032-.0972L6.973 9.8356l-2.55-1.6879-1.3356-.9714-.7225-.4918-.3643-.4614-.1578-1.0078.6557-.7225.8803.0607.2246.0607.8925.686 1.9064 1.4754 2.4893 1.8336.3643.3035.1457-.1032.0182-.0728-.164-.2733-1.3539-2.4467-1.445-2.4893-.6435-1.032-.17-.6194c-.0607-.255-.1032-.4674-.1032-.7285L6.287.1335 6.6997 0l.9957.1336.419.3642.6192 1.4147 1.0018 2.2282 1.5543 3.0296.4553.8985.2429.8318.091.255h.1579v-.1457l.1275-1.706.2368-2.0947.2307-2.6957.0789-.7589.3764-.9107.7468-.4918.5828.2793.4797.686-.0668.4433-.2853 1.8517-.5586 2.9021-.3643 1.9429h.2125l.2429-.2429.9835-1.3053 1.6514-2.0643.7286-.8196.85-.9046.5464-.4311h1.0321l.759 1.1293-.34 1.1657-1.0625 1.3478-.8804 1.1414-1.2628 1.7-.7893 1.36.0729.1093.1882-.0183 2.8535-.607 1.5421-.2794 1.8396-.3157.8318.3886.091.3946-.3278.8075-1.967.4857-2.3072.4614-3.4364.8136-.0425.0304.0486.0607 1.5482.1457.6618.0364h1.621l3.0175.2247.7892.522.4736.6376-.079.4857-1.2142.6193-1.6393-.3886-3.825-.9107-1.3113-.3279h-.1822v.1093l1.0929 1.0686 2.0035 1.8092 2.5075 2.3314.1275.5768-.3218.4554-.34-.0486-2.2039-1.6575-.85-.7468-1.9246-1.621h-.1275v.17l.4432.6496 2.3436 3.5214.1214 1.0807-.17.3521-.6071.2125-.6679-.1214-1.3721-1.9246L14.38 17.959l-1.1414-1.9428-.1397.079-.674 7.2552-.3156.3703-.7286.2793-.6071-.4614-.3218-.7468.3218-1.4753.3886-1.9246.3157-1.53.2853-1.9004.17-.6314-.0121-.0425-.1397.0182-1.4328 1.9672-2.1796 2.9446-1.7243 1.8456-.4128.164-.7164-.3704.0667-.6618.4008-.5889 2.386-3.0357 1.4389-1.882.929-1.0868-.0062-.1579h-.0546l-6.3385 4.1164-1.1293.1457-.4857-.4554.0608-.7467.2307-.2429 1.9064-1.3114Z"/>
      </g>
    </svg>"""
}

FINAL_ORDER = [
    # Linha 1 (12 ícones): Web, Linguagens e Engines/3D
    "html", "css", "js", "ts", "react", "nextjs",
    "c", "cpp", "java", "py", "construct3", "gamemaker",
    # Linha 2 (12 ícones): 3D, Design, Bancos/BaaS, Ferramentas & IA
    "blender", "figma", "supabase", "firebase", "postgres", "mysql",
    "git", "github", "vscode", "antigravity", "codex", "claude"
]

def build_unified_svg():
    tiles = fetch_skillicons_tiles()
    tiles.update(EXTRA_TILES)

    perline = 12
    rows = 2
    step = 300
    tile_w = 256

    view_w = (perline - 1) * step + tile_w
    view_h = (rows - 1) * step + tile_w

    # Escala de exibição confortável (~680px de largura)
    disp_w = 680
    disp_h = int(disp_w * (view_h / view_w))

    groups = []
    for idx, key in enumerate(FINAL_ORDER):
        col = idx % perline
        row = idx // perline
        x = col * step
        y = row * step
        groups.append(f'  <g transform="translate({x}, {y})">\n    {tiles[key]}\n  </g>')

    full_svg = (
        f'<svg width="{disp_w}" height="{disp_h}" viewBox="0 0 {view_w} {view_h}" '
        f'fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">\n'
        + "\n".join(groups)
        + "\n</svg>\n"
    )

    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(full_svg)
    print(f"Gerado {OUTPUT_SVG} com {len(FINAL_ORDER)} ícones unificados!")

if __name__ == "__main__":
    build_unified_svg()
