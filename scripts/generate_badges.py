import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


def make_badge_svg(filename, left_text, right_text, right_bg, icon_svg_path, left_w, right_w):
    total_w = left_w + right_w
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="32" viewBox="0 0 {total_w} 32" fill="none">
  <rect width="{total_w}" height="32" rx="6" fill="#0D1117"/>
  <path d="M {left_w} 0 H {total_w - 6} A 6 6 0 0 1 {total_w} 6 V 26 A 6 6 0 0 1 {total_w - 6} 32 H {left_w} Z" fill="{right_bg}"/>
  <rect x="0.5" y="0.5" width="{total_w - 1}" height="31" rx="5.5" stroke="#30363D"/>
  <g transform="translate(10, 7)">
    {icon_svg_path}
  </g>
  <text x="{32 + (left_w - 32) / 2:.1f}" y="20" text-anchor="middle" fill="#F0F6FC" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="700" font-size="11" letter-spacing="0.8">{left_text}</text>
  <text x="{left_w + right_w / 2:.1f}" y="20" text-anchor="middle" fill="#FFFFFF" font-family="Segoe UI, Ubuntu, sans-serif" font-weight="700" font-size="11" letter-spacing="0.8">{right_text}</text>
</svg>
"""
    with open(os.path.join(ASSETS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(svg)


def generate_all_badges():
    # 1. Inatel - Software Engineering
    icon_grad = '<path fill="#567599" d="M9 1.5L0 6l9 4.5 7.36-3.68v5.18H18V6L9 1.5zm0 11.25l-5.4-2.7v3.6L9 16.5l5.4-2.85v-3.6L9 12.75z"/>'
    make_badge_svg("badge-inatel.svg", "INATEL", "SOFTWARE ENGINEERING", "#567599", icon_grad, 88, 178)

    # 2. Made By You - Co-Founder
    icon_rocket = '<path fill="#0088FF" d="M9 1C5.5 3.2 4 7.5 4 11l2.5 2.5C9.5 13.5 13.8 12 16 8.5 16.5 4.5 13 0.5 9 1zm1.5 5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0zM3.5 12.5L1 15l2 2 2.5-2.5-2-2z"/>'
    make_badge_svg("badge-mby.svg", "MADE BY YOU", "CO-FOUNDER", "#0088FF", icon_rocket, 122, 108)

    # 3. CP2eJr - Member
    icon_code = '<path fill="#F79C1D" d="M5.5 3L0.5 9l5 6 1.3-1.1L2.7 9l4.1-4.9L5.5 3zm7 0l-1.3 1.1L15.3 9l-4.1 4.9 1.3 1.1 5-6-5-6zM10.2 2l-3.2 14h1.6l3.2-14h-1.6z"/>'
    make_badge_svg("badge-cp2ejr.svg", "CP2EJR", "MEMBER", "#F79C1D", icon_code, 86, 82)

    # 4. Focus - Software • Games • 3D
    icon_cube = '<path fill="#38BDF8" d="M9 1L1.5 5.2v8.6L9 18l7.5-4.2V5.2L9 1zm0 2.1l5.2 2.9L9 8.9 3.8 6 9 3.1zM3.3 7.5l4.8 2.7v5.5l-4.8-2.7V7.5zm6.6 8.2v-5.5l4.8-2.7v5.5l-4.8 2.7z"/>'
    make_badge_svg("badge-focus.svg", "FOCUS", "SOFTWARE • GAMES • 3D", "#1F6FEB", icon_cube, 80, 176)

    # --- BOTÕES DE CONTATO DO RODAPÉ ---
    # 5. LinkedIn
    icon_linkedin = '<path fill="#0088FF" d="M15.3 1H2.7C1.76 1 1 1.76 1 2.7v12.6c0 .94.76 1.7 1.7 1.7h12.6c.94 0 1.7-.76 1.7-1.7V2.7c0-.94-.76-1.7-1.7-1.7zM5.8 14.5H3.4V7h2.4v7.5zM4.6 5.95c-.78 0-1.4-.63-1.4-1.4 0-.78.62-1.4 1.4-1.4.77 0 1.4.62 1.4 1.4 0 .77-.63 1.4-1.4 1.4zm10 8.55h-2.4v-3.7c0-.88-.02-2.02-1.23-2.02-1.23 0-1.42.96-1.42 1.95v3.77H7.15V7h2.3v1.02h.03c.32-.6 1.1-1.23 2.27-1.23 2.43 0 2.88 1.6 2.88 3.68v4.03z"/>'
    make_badge_svg("btn-linkedin.svg", "LINKEDIN", "/in/vitor-noronha", "#0088FF", icon_linkedin, 102, 136)

    # 6. Email (Gmail)
    icon_mail = '<path fill="#F79C1D" d="M2 3h14a1.5 1.5 0 0 1 1.5 1.5v9A1.5 1.5 0 0 1 16 15H2a1.5 1.5 0 0 1-1.5-1.5v-9A1.5 1.5 0 0 1 2 3zm0 2v.4l7 4.4 7-4.4V5l-7 4.4L2 5z"/>'
    make_badge_svg("btn-email.svg", "E-MAIL", "vitorhugo.noronha15@gmail.com", "#F79C1D", icon_mail, 86, 224)

    # 7. GitHub
    icon_github = '<path fill="#38BDF8" fill-rule="evenodd" d="M9 1C4.58 1 1 4.58 1 9c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 17 9c0-4.42-3.58-8-8-8z"/>'
    make_badge_svg("btn-github.svg", "GITHUB", "XkrulesVitor", "#238636", icon_github, 88, 108)

    print("Todos os badges SVG com ícones vetoriais gerados com sucesso!")


if __name__ == "__main__":
    generate_all_badges()
