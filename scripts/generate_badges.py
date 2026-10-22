import io
import os
import resvg_py
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = r"C:\Windows\Fonts"


def create_retina_badge(
    filename,
    left_text,
    right_text,
    right_bg_rgb,
    logo_img=None,
    svg_icon_str=None,
    height=64  # 2x Retina (exibido a 32px de altura no README)
):
    font = ImageFont.truetype(os.path.join(FONTS_DIR, "segoeuib.ttf"), 22)
    dummy = Image.new("RGBA", (10, 10))
    ddraw = ImageDraw.Draw(dummy)

    lb = ddraw.textbbox((0, 0), left_text, font=font)
    rb = ddraw.textbbox((0, 0), right_text, font=font)
    lw_txt = lb[2] - lb[0]
    rw_txt = rb[2] - rb[0]

    icon_slot = 54 if (logo_img is not None or svg_icon_str is not None) else 16
    left_w = icon_slot + lw_txt + 28
    right_w = rw_txt + 36
    total_w = left_w + right_w

    # Renderiza com supersampling 2x adicional para bordas perfeitas
    ss = 2
    W, H = total_w * ss, height * ss
    LW = left_w * ss
    R = 12 * ss

    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # Fundo esquerdo (#0d1117)
    draw.rounded_rectangle((0, 0, W - 1, H - 1), radius=R, fill=(13, 17, 23, 255))

    # Fundo direito colorido (com cantos direitos arredondados)
    right_mask = Image.new("L", (W, H), 0)
    rm_draw = ImageDraw.Draw(right_mask)
    rm_draw.rounded_rectangle((0, 0, W - 1, H - 1), radius=R, fill=255)
    rm_draw.rectangle((0, 0, LW, H), fill=0)

    right_layer = Image.new("RGBA", (W, H), (*right_bg_rgb, 255))
    canvas.paste(right_layer, (0, 0), right_mask)

    # Borda sutil (#30363d)
    draw.rounded_rectangle((1, 1, W - 2, H - 2), radius=R, outline=(48, 54, 61, 255), width=2)

    # Reduz para resolução 2x Retina final
    out = canvas.resize((total_w, height), Image.Resampling.LANCZOS)
    out_draw = ImageDraw.Draw(out)

    # Cola o ícone ou logo à esquerda do texto
    if logo_img is not None:
        bbox = logo_img.getbbox()
        if bbox:
            logo_img = logo_img.crop(bbox)
        iw, ih = logo_img.size
        max_w, max_h = 38, 38
        scale = min(max_w / iw, max_h / ih)
        nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
        resized_logo = logo_img.resize((nw, nh), Image.Resampling.LANCZOS)
        ix = 14 + (38 - nw) // 2
        iy = (height - nh) // 2
        out.alpha_composite(resized_logo, (ix, iy))
    elif svg_icon_str is not None:
        full_svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 18 18" fill="none">{svg_icon_str}</svg>'
        png_bytes = resvg_py.svg_to_bytes(full_svg, width=36, height=36)
        icon_im = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        out.alpha_composite(icon_im, (15, (height - 36) // 2))

    # Desenha textos centralizados verticalmente
    ly = (height - (lb[3] - lb[1])) // 2 - lb[1] - 1
    ry = (height - (rb[3] - rb[1])) // 2 - rb[1] - 1

    out_draw.text((icon_slot + 10, ly), left_text, font=font, fill=(240, 246, 252, 255))
    out_draw.text((left_w + (right_w - rw_txt) // 2, ry), right_text, font=font, fill=(255, 255, 255, 255))

    out_path = os.path.join(ASSETS_DIR, filename)
    out.save(out_path, "PNG")
    return out


def main():
    mby_logo = Image.open(os.path.join(ASSETS_DIR, "mby.png")).convert("RGBA")
    cp2_logo = Image.open(os.path.join(ASSETS_DIR, "cp2ejr.png")).convert("RGBA")

    # 1. Inatel
    icon_grad = '<path fill="#567599" d="M9 1.5L0 6l9 4.5 7.36-3.68v5.18H18V6L9 1.5zm0 11.25l-5.4-2.7v3.6L9 16.5l5.4-2.85v-3.6L9 12.75z"/>'
    b1 = create_retina_badge("badge-inatel.png", "INATEL", "SOFTWARE ENGINEERING", (86, 117, 153), svg_icon_str=icon_grad)

    # 2. Made By You (com a logo real da MBY à esquerda!)
    b2 = create_retina_badge("badge-mby.png", "MADE BY YOU", "CO-FOUNDER", (0, 136, 255), logo_img=mby_logo)

    # 3. CP2eJr (com a logo real da CP2eJr à esquerda e cargo COORDENADOR!)
    b3 = create_retina_badge("badge-cp2ejr.png", "CP2EJR", "COORDENADOR", (247, 156, 29), logo_img=cp2_logo)

    # 4. Focus (Front-End • Software • Games & 3D)
    icon_cube = '<path fill="#38BDF8" d="M9 1L1.5 5.2v8.6L9 18l7.5-4.2V5.2L9 1zm0 2.1l5.2 2.9L9 8.9 3.8 6 9 3.1zM3.3 7.5l4.8 2.7v5.5l-4.8-2.7V7.5zm6.6 8.2v-5.5l4.8-2.7v5.5l-4.8 2.7z"/>'
    b4 = create_retina_badge("badge-focus.png", "FOCUS", "FRONT-END • SOFTWARE • GAMES & 3D", (31, 111, 235), svg_icon_str=icon_cube)

    # Botões de contato do rodapé
    icon_linkedin = '<path fill="#0088FF" d="M15.3 1H2.7C1.76 1 1 1.76 1 2.7v12.6c0 .94.76 1.7 1.7 1.7h12.6c.94 0 1.7-.76 1.7-1.7V2.7c0-.94-.76-1.7-1.7-1.7zM5.8 14.5H3.4V7h2.4v7.5zM4.6 5.95c-.78 0-1.4-.63-1.4-1.4 0-.78.62-1.4 1.4-1.4.77 0 1.4.62 1.4 1.4 0 .77-.63 1.4-1.4 1.4zm10 8.55h-2.4v-3.7c0-.88-.02-2.02-1.23-2.02-1.23 0-1.42.96-1.42 1.95v3.77H7.15V7h2.3v1.02h.03c.32-.6 1.1-1.23 2.27-1.23 2.43 0 2.88 1.6 2.88 3.68v4.03z"/>'
    c1 = create_retina_badge("btn-linkedin.png", "LINKEDIN", "/in/vitor-noronha", (0, 136, 255), svg_icon_str=icon_linkedin)

    icon_mail = '<path fill="#F79C1D" d="M2 3h14a1.5 1.5 0 0 1 1.5 1.5v9A1.5 1.5 0 0 1 16 15H2a1.5 1.5 0 0 1-1.5-1.5v-9A1.5 1.5 0 0 1 2 3zm0 2v.4l7 4.4 7-4.4V5l-7 4.4L2 5z"/>'
    c2 = create_retina_badge("btn-email.png", "E-MAIL", "vitorhugo.noronha15@gmail.com", (247, 156, 29), svg_icon_str=icon_mail)

    icon_github = '<path fill="#38BDF8" fill-rule="evenodd" d="M9 1C4.58 1 1 4.58 1 9c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 17 9c0-4.42-3.58-8-8-8z"/>'
    c3 = create_retina_badge("btn-github.png", "GITHUB", "XkrulesVitor", (0, 136, 255), svg_icon_str=icon_github)

    # Cria imagem de preview combinada para inspeção
    preview = Image.new("RGBA", (1200, 170), (13, 17, 23, 255))
    x = 20
    for b in [b1, b2, b3]:
        preview.alpha_composite(b, (x, 16))
        x += b.size[0] + 16
    x = 20
    for b in [b4, c1, c2, c3]:
        if x + b.size[0] < 1180:
            preview.alpha_composite(b, (x, 94))
            x += b.size[0] + 16
    preview.save(os.path.join(ASSETS_DIR, "badges_preview.png"))
    print("Badges 2x Retina gerados com sucesso!")


if __name__ == "__main__":
    main()
