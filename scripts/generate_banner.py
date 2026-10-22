import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageChops

# Caminhos de entrada e saída
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CP2EJR_PATH = os.path.join(ASSETS_DIR, "cp2ejr.png")
MBY_PATH = os.path.join(ASSETS_DIR, "mby.png")
OUTPUT_GIF = os.path.join(ASSETS_DIR, "banner.gif")
OUTPUT_WEBP = os.path.join(ASSETS_DIR, "banner.webp")
PREVIEW_PNG = os.path.join(ASSETS_DIR, "preview_frames.png")

# Dimensões do banner (proporção panorâmica ideal para topo de README do GitHub)
WIDTH = 960
HEIGHT = 300

# Paleta de cores unificada (GitHub Dark + CP2eJr Steel/Orange + Made By You Azure Blue)
BG_DARK = (13, 17, 23)          # #0d1117 (GitHub Dark Mode nativo)
CARD_BG = (22, 27, 34)          # #161b22
BORDER_COL = (48, 54, 61)       # #30363d
CP_BLUE = (86, 117, 153)        # #567599 (Azul aço CP2eJr)
CP_ORANGE = (247, 156, 29)      # #f79c1d (Laranja vibrante CP2eJr)
MBY_BLUE = (0, 136, 255)        # #0088ff (Azul elétrico Made By You)
MBY_CYAN = (56, 189, 248)       # #38bdf8 (Ciano brilhante)
TEXT_WHITE = (240, 246, 252)    # #f0f6fc
TEXT_MUTED = (139, 148, 158)    # #8b949e


def solve_linear_system_8x8(A, B):
    """Resolve um sistema linear 8x8 via eliminação gaussiana com pivoteamento parcial."""
    n = 8
    M = [row[:] + [B[i]] for i, row in enumerate(A)]
    for col in range(n):
        max_row = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[max_row] = M[max_row], M[col]
        pivot = M[col][col]
        if abs(pivot) < 1e-12:
            pivot = 1e-12
        for j in range(col, n + 1):
            M[col][j] /= pivot
        for r in range(n):
            if r != col:
                factor = M[r][col]
                for j in range(col, n + 1):
                    M[r][j] -= factor * M[col][j]
    return [M[i][n] for i in range(n)]


def find_perspective_coeffs(src_pts, dst_pts):
    """
    Calcula os 8 coeficientes para Image.Transform.PERSPECTIVE
    que mapeiam dst_pts (na imagem de saída) para src_pts (na imagem de origem).
    """
    matrix = []
    rhs = []
    for (x, y), (X, Y) in zip(src_pts, dst_pts):
        matrix.append([X, Y, 1, 0, 0, 0, -x * X, -x * Y])
        matrix.append([0, 0, 0, X, Y, 1, -y * X, -y * Y])
        rhs.append(x)
        rhs.append(y)
    return solve_linear_system_8x8(matrix, rhs)


def prepare_square_logo(img_path, canvas_size=240, logo_max_w=175, logo_max_h=125):
    """Carrega uma logo RGBA e centraliza em um canvas quadrado transparente."""
    im = Image.open(img_path).convert("RGBA")
    # Recorta bordas transparentes extras se existirem
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    scale = min(logo_max_w / w, logo_max_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)

    sq = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    sq.paste(im, ((canvas_size - new_w) // 2, (canvas_size - new_h) // 2), im)
    return sq


def make_tinted_layer(sq_logo, color_rgb, brightness=0.85):
    """Cria uma versão colorida/sombreada da logo para formar a espessura 3D extrudada."""
    r, g, b, a = sq_logo.split()
    tinted = Image.new("RGBA", sq_logo.size, (
        int(color_rgb[0] * brightness),
        int(color_rgb[1] * brightness),
        int(color_rgb[2] * brightness),
        255
    ))
    tinted.putalpha(a)
    return tinted


def project_3d_quad(S, z_offset, theta_y, theta_x, theta_z, focal=520.0):
    """Projeta os 4 cantos do quadrado SxS no espaço 3D para coordenadas 2D."""
    R = S / 2.0
    corners_3d = [
        (-R, -R, z_offset),
        ( R, -R, z_offset),
        ( R,  R, z_offset),
        (-R,  R, z_offset),
    ]
    cy, sy = math.cos(theta_y), math.sin(theta_y)
    cx, sx = math.cos(theta_x), math.sin(theta_x)
    cz, sz = math.cos(theta_z), math.sin(theta_z)

    pts_2d = []
    for x, y, z in corners_3d:
        # Rotação em Y (giro 3D principal)
        x1 = x * cy + z * sy
        y1 = y
        z1 = -x * sy + z * cy
        # Rotação em X (inclinação 3D)
        x2 = x1
        y2 = y1 * cx - z1 * sx
        z2 = y1 * sx + z1 * cx
        # Rotação em Z (flutuação suave)
        x3 = x2 * cz - y2 * sz
        y3 = x2 * sz + y2 * cz
        z3 = z2

        scale = focal / (focal + z3)
        X = (S / 2.0) + x3 * scale
        Y = (S / 2.0) + y3 * scale
        pts_2d.append((X, Y))
    return pts_2d


def render_3d_extruded_logo(sq_logo, edge_layers_imgs, theta_y, theta_x, theta_z, thickness=14.0):
    """
    Renderiza a logo com extrusão 3D real (múltiplas camadas de profundidade em perspectiva)
    e iluminação dinâmica conforme o ângulo de rotação.
    """
    S = sq_logo.size[0]
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    cos_y = math.cos(theta_y)

    # Se a face traseira está voltada para a câmera, espelhamos horizontalmente a textura
    # para que a moeda/emblema 3D seja legível de ambos os lados
    front_facing = cos_y >= 0
    if front_facing:
        src_pts = [(0, 0), (S, 0), (S, S), (0, S)]
    else:
        src_pts = [(S, 0), (0, 0), (0, S), (S, S)]

    num_slices = len(edge_layers_imgs)
    # Ordena as fatias Z da mais distante para a mais próxima da câmera
    z_values = [
        -thickness / 2.0 + i * (thickness / max(1, num_slices - 1))
        for i in range(num_slices)
    ]
    if not front_facing:
        z_values.reverse()

    # Renderiza as fatias laterais (corpo 3D extrudado contínuo)
    for idx, z_val in enumerate(z_values[:-1]):
        dst_pts = project_3d_quad(S, z_val, theta_y, theta_x, theta_z)
        coeffs = find_perspective_coeffs(src_pts, dst_pts)
        slice_img = edge_layers_imgs[idx].transform(
            (S, S), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BILINEAR
        )
        out.alpha_composite(slice_img)

    # Renderiza a face frontal visível com brilho especular dinâmico
    top_z = z_values[-1]
    dst_pts = project_3d_quad(S, top_z, theta_y, theta_x, theta_z)
    coeffs = find_perspective_coeffs(src_pts, dst_pts)

    # Brilho varia suavemente com o ângulo para dar sensação de reflexo de luz 3D
    light_factor = 0.90 + 0.25 * abs(cos_y)
    lit_logo = ImageEnhance.Brightness(sq_logo).enhance(light_factor)
    face_img = lit_logo.transform(
        (S, S), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC
    )
    out.alpha_composite(face_img)
    return out


def create_base_background():
    """Cria o background estático otimizado com estética Cyberpunk/Sci-Fi Dark Mode."""
    bg = Image.new("RGBA", (WIDTH, HEIGHT), (*BG_DARK, 255))
    draw = ImageDraw.Draw(bg)

    # Grade de perspectiva sutil no piso e topo
    grid_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid_layer)

    # Linhas horizontais sutis
    for y in range(25, HEIGHT - 20, 30):
        gdraw.line([(20, y), (WIDTH - 20, y)], fill=(48, 54, 61, 28), width=1)
    # Linhas verticais sutis
    for x in range(40, WIDTH - 20, 40):
        gdraw.line([(x, 20), (x, HEIGHT - 20)], fill=(48, 54, 61, 22), width=1)

    bg.alpha_composite(grid_layer)

    # Glow radial esquerdo (cores da CP2eJr: Azul Aço + Laranja)
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.ellipse((35, 45, 255, 255), fill=(*CP_BLUE, 42))
    glow_draw.ellipse((85, 95, 225, 215), fill=(*CP_ORANGE, 35))

    # Glow radial direito (cores da Made By You: Azul Elétrico)
    glow_draw.ellipse((WIDTH - 255, 45, WIDTH - 35, 255), fill=(*MBY_BLUE, 48))
    glow_draw.ellipse((WIDTH - 215, 85, WIDTH - 75, 215), fill=(*MBY_CYAN, 30))

    # Glow central sutil atrás do texto
    glow_draw.ellipse((290, 60, WIDTH - 290, HEIGHT - 60), fill=(30, 55, 90, 28))

    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=36))
    bg.alpha_composite(glow_layer)

    # Moldura externa arredondada elegante com borda dupla sutil
    frame_draw = ImageDraw.Draw(bg)
    frame_draw.rounded_rectangle(
        (8, 8, WIDTH - 9, HEIGHT - 9),
        radius=18,
        outline=BORDER_COL,
        width=2
    )
    # Detalhes de luz nos cantos (Laranja CP2eJr à esquerda, Azul MBY à direita)
    frame_draw.arc((8, 8, 44, 44), start=180, end=270, fill=CP_ORANGE, width=3)
    frame_draw.arc((8, HEIGHT - 45, 44, HEIGHT - 9), start=90, end=180, fill=CP_BLUE, width=3)
    frame_draw.arc((WIDTH - 45, 8, WIDTH - 9, 44), start=270, end=360, fill=MBY_BLUE, width=3)
    frame_draw.arc((WIDTH - 45, HEIGHT - 45, WIDTH - 9, HEIGHT - 9), start=0, end=90, fill=MBY_CYAN, width=3)

    return bg


def get_typing_state(frame_idx, total_frames):
    """
    Retorna (texto_atual, modo_nick, cursor_visivel) para o frame atual.
    Sequência pedida:
    1. Digita 'Vitor Hugo Felipe Noronha'
    2. Pausa curta lendo
    3. Apaga tudo
    4. Digita 'XKrules'
    5. Pausa curta lendo
    6. Apaga tudo e termina (recomeçando o loop)
    """
    full_name = "Vitor Hugo Felipe Noronha"
    nick = "XKrules"

    # Total = 160 frames (a 20 fps = 8.0 segundos por ciclo completo)
    # 0..50: digitando Vitor Hugo Felipe Noronha (25 chars -> 2 frames por char)
    # 50..78: mantém Vitor Hugo Felipe Noronha (1.4s)
    # 78..103: apagando Vitor Hugo Felipe Noronha (25 chars -> 1 frame por char)
    # 103..109: pausa vazio (0.3s)
    # 109..123: digitando XKrules (7 chars -> 2 frames por char)
    # 123..147: mantém XKrules (1.2s)
    # 147..154: apagando XKrules (7 chars -> 1 frame por char)
    # 154..160: pausa vazio antes de recomeçar (0.3s)

    cursor_blink = (frame_idx // 5) % 2 == 0

    if frame_idx < 50:
        chars = (frame_idx + 1) // 2
        return full_name[:chars], False, True
    elif frame_idx < 78:
        return full_name, False, cursor_blink
    elif frame_idx < 103:
        rem = 25 - (frame_idx - 78)
        return full_name[:max(0, rem)], False, True
    elif frame_idx < 109:
        return "", False, cursor_blink
    elif frame_idx < 123:
        chars = (frame_idx - 109 + 1) // 2
        return nick[:chars], True, True
    elif frame_idx < 147:
        return nick, True, cursor_blink
    elif frame_idx < 154:
        rem = 7 - (frame_idx - 147)
        return nick[:max(0, rem)], True, True
    else:
        return "", False, cursor_blink


def generate_banner():
    print("Preparando logos e camadas 3D...")
    cp_sq = prepare_square_logo(CP2EJR_PATH, canvas_size=230, logo_max_w=175, logo_max_h=120)
    mby_sq = prepare_square_logo(MBY_PATH, canvas_size=230, logo_max_w=175, logo_max_h=125)

    # Mini-logos para o cardzinho inferior dentro do GIF
    cp_mini = prepare_square_logo(CP2EJR_PATH, canvas_size=24, logo_max_w=22, logo_max_h=16)
    mby_mini = prepare_square_logo(MBY_PATH, canvas_size=24, logo_max_w=22, logo_max_h=16)

    # Cria 24 camadas de profundidade para extrusão 3D sólida e contínua de cada logo
    cp_edges = []
    mby_edges = []
    num_depth = 24
    for i in range(num_depth):
        # Gradiente lateral entre azul-aço e laranja para CP2eJr
        t_col = i / max(1, num_depth - 1)
        c_r = int(CP_BLUE[0] * (1 - t_col) + CP_ORANGE[0] * t_col)
        c_g = int(CP_BLUE[1] * (1 - t_col) + CP_ORANGE[1] * t_col)
        c_b = int(CP_BLUE[2] * (1 - t_col) + CP_ORANGE[2] * t_col)
        cp_edges.append(make_tinted_layer(cp_sq, (c_r, c_g, c_b), brightness=0.55 + 0.25 * t_col))

        # Gradiente lateral entre azul profundo e ciano neon para Made By You
        m_r = int(10 * (1 - t_col) + MBY_CYAN[0] * t_col)
        m_g = int(75 * (1 - t_col) + MBY_CYAN[1] * t_col)
        m_b = int(165 * (1 - t_col) + MBY_CYAN[2] * t_col)
        mby_edges.append(make_tinted_layer(mby_sq, (m_r, m_g, m_b), brightness=0.55 + 0.3 * t_col))

    base_bg = create_base_background()

    # Carrega fontes do Windows
    fonts_dir = r"C:\Windows\Fonts"
    font_name = ImageFont.truetype(os.path.join(fonts_dir, "segoeuib.ttf"), 32)
    font_nick = ImageFont.truetype(os.path.join(fonts_dir, "segoeuib.ttf"), 48)
    font_mono_top = ImageFont.truetype(os.path.join(fonts_dir, "consolab.ttf"), 13)
    font_sub = ImageFont.truetype(os.path.join(fonts_dir, "segoeui.ttf"), 14)
    font_badge = ImageFont.truetype(os.path.join(fonts_dir, "consolab.ttf"), 12)

    total_frames = 160
    frames = []

    # Partículas de fundo (posições base determinísticas)
    particles = [
        (110, 55, 2.0, CP_ORANGE, 0.0),
        (185, 240, 2.5, CP_BLUE, 1.2),
        (75, 215, 2.0, CP_ORANGE, 2.5),
        (225, 70, 1.8, CP_BLUE, 3.8),
        (745, 65, 2.2, MBY_CYAN, 0.7),
        (880, 80, 2.0, MBY_BLUE, 2.1),
        (770, 235, 2.5, MBY_BLUE, 4.0),
        (865, 220, 1.8, MBY_CYAN, 5.1),
        (330, 48, 1.5, CP_BLUE, 1.5),
        (630, 52, 1.5, MBY_BLUE, 3.2),
        (360, 252, 1.5, CP_ORANGE, 4.5),
        (600, 248, 1.5, MBY_CYAN, 0.4),
    ]

    print(f"Renderizando {total_frames} frames em 3D...")
    for f in range(total_frames):
        t = (f + 0.5) / float(total_frames)
        angle = 2.0 * math.pi * t

        frame = base_bg.copy()
        draw = ImageDraw.Draw(frame)

        # 1. Partículas flutuantes suaves
        for px, py, pr, pcol, phase in particles:
            dy = 7.0 * math.sin(angle + phase)
            alpha = int(110 + 90 * math.sin(angle * 2 + phase))
            p_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            p_draw = ImageDraw.Draw(p_layer)
            p_draw.ellipse((px - pr, py + dy - pr, px + pr, py + dy + pr), fill=(*pcol, alpha))
            frame.alpha_composite(p_layer)

        # 2. Anéis holográficos 3D na base de cada logo (pulsam com a altura da flutuação)
        float_left = 11.0 * math.sin(angle)
        float_right = 11.0 * math.sin(angle + math.pi)  # Fase oposta para equilíbrio dinâmico

        ring_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        rdraw = ImageDraw.Draw(ring_layer)

        # Anel de energia abaixo da CP2eJr (x=140, y=248)
        rw_l = int(58 - float_left * 0.8)
        rh_l = int(11 - float_left * 0.15)
        rdraw.ellipse((140 - rw_l, 248 - rh_l, 140 + rw_l, 248 + rh_l), outline=(*CP_ORANGE, 115), width=2)
        rdraw.ellipse((140 - rw_l + 14, 248 - rh_l + 3, 140 + rw_l - 14, 248 + rh_l - 3), outline=(*CP_BLUE, 90), width=1)

        # Anel de energia abaixo da Made By You (x=820, y=248)
        rw_r = int(58 - float_right * 0.8)
        rh_r = int(11 - float_right * 0.15)
        rdraw.ellipse((820 - rw_r, 248 - rh_r, 820 + rw_r, 248 + rh_r), outline=(*MBY_BLUE, 130), width=2)
        rdraw.ellipse((820 - rw_r + 14, 248 - rh_r + 3, 820 + rw_r - 14, 248 + rh_r - 3), outline=(*MBY_CYAN, 95), width=1)

        frame.alpha_composite(ring_layer)

        # 3. Renderiza as duas logos 3D girando e flutuando
        # CP2eJr à esquerda: gira 360° em Y + leve inclinação 3D em X e Z
        cp_3d = render_3d_extruded_logo(
            cp_sq,
            cp_edges,
            theta_y=angle,
            theta_x=0.22 * math.cos(angle),
            theta_z=0.08 * math.sin(angle),
            thickness=13.5
        )
        cp_x = int(140 - cp_3d.size[0] // 2)
        cp_y = int(142 + float_left - cp_3d.size[1] // 2)
        frame.alpha_composite(cp_3d, (cp_x, cp_y))

        # Made By You à direita: gira 360° em Y no sentido simétrico + inclinação 3D
        mby_3d = render_3d_extruded_logo(
            mby_sq,
            mby_edges,
            theta_y=-angle,
            theta_x=0.22 * math.sin(angle),
            theta_z=-0.08 * math.cos(angle),
            thickness=13.5
        )
        mby_x = int(820 - mby_3d.size[0] // 2)
        mby_y = int(142 + float_right - mby_3d.size[1] // 2)
        frame.alpha_composite(mby_3d, (mby_x, mby_y))

        # 4. Área central: Header, Texto Digitado (Vitor Hugo Felipe Noronha / XKrules) e Subtítulo
        center_x = WIDTH // 2

        # Tag superior estilo terminal / sci-fi
        top_tag = "< SOFTWARE ENGINEERING @ INATEL • GAME DEV • 3D />"
        tb = draw.textbbox((0, 0), top_tag, font=font_mono_top)
        tw = tb[2] - tb[0]
        draw.text((center_x - tw // 2, 58), top_tag, font=font_mono_top, fill=MBY_CYAN)

        # Linha decorativa superior sutil com gradiente nas pontas
        draw.line([(center_x - 160, 84), (center_x - 10, 84)], fill=CP_ORANGE, width=2)
        draw.line([(center_x + 10, 84), (center_x + 160, 84)], fill=MBY_BLUE, width=2)
        draw.ellipse((center_x - 3, 81, center_x + 3, 87), fill=TEXT_WHITE)

        # Texto sendo digitado no centro
        curr_text, is_nick, show_cursor = get_typing_state(f, total_frames)
        active_font = font_nick if is_nick else font_name

        # Mede largura do texto atual para centralizar perfeitamente
        if curr_text:
            bbox = draw.textbbox((0, 0), curr_text, font=active_font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        else:
            text_w = 0
            bbox_ref = draw.textbbox((0, 0), "A", font=active_font)
            text_h = bbox_ref[3] - bbox_ref[1]

        text_x = center_x - text_w // 2
        text_y = 136 - text_h // 2 - (6 if is_nick else 0)

        if curr_text:
            # Sombra suave / glow atrás do texto
            glow_txt = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            gtdraw = ImageDraw.Draw(glow_txt)
            glow_col = (*MBY_BLUE, 120) if is_nick else (*CP_BLUE, 95)
            gtdraw.text((text_x, text_y + 2), curr_text, font=active_font, fill=glow_col)
            glow_txt = glow_txt.filter(ImageFilter.GaussianBlur(radius=6))
            frame.alpha_composite(glow_txt)

            # Se for o nick XKrules, destaca "XK" em Laranja CP2eJr e "rules" em Azul MBY/Branco Brilhante
            if is_nick:
                xk_part = curr_text[:2]
                rest_part = curr_text[2:]
                draw.text((text_x, text_y), xk_part, font=active_font, fill=CP_ORANGE)
                if rest_part:
                    xk_b = draw.textbbox((0, 0), xk_part, font=active_font)
                    xk_w = xk_b[2] - xk_b[0]
                    draw.text((text_x + xk_w, text_y), rest_part, font=active_font, fill=MBY_CYAN)
            else:
                draw.text((text_x, text_y), curr_text, font=active_font, fill=TEXT_WHITE)

        # Cursor piscante ao lado do texto
        if show_cursor:
            cursor_x = text_x + text_w + 5
            cursor_top = 122 if not is_nick else 116
            cursor_bot = 160 if not is_nick else 166
            cursor_col = CP_ORANGE if is_nick else MBY_BLUE
            draw.rounded_rectangle(
                (cursor_x, cursor_top, cursor_x + 4, cursor_bot),
                radius=2,
                fill=cursor_col
            )

        # Badges inferiores com mini-logos ([logo] CP2eJr • [logo] Co-Founder @ Made By You)
        sub_y = 204
        pill_w, pill_h = 446, 32
        px1 = center_x - pill_w // 2
        py1 = sub_y
        draw.rounded_rectangle(
            (px1, py1, px1 + pill_w, py1 + pill_h),
            radius=16,
            fill=CARD_BG,
            outline=BORDER_COL,
            width=1
        )

        badge_left = "CP2eJr"
        badge_sep = "   •   "
        badge_right = "Co-Founder @ Made By You"

        b1_w = draw.textbbox((0, 0), badge_left, font=font_badge)[2]
        sep_w = draw.textbbox((0, 0), badge_sep, font=font_badge)[2]
        b2_w = draw.textbbox((0, 0), badge_right, font=font_badge)[2]
        logo_slot = 26

        total_inner_w = logo_slot + b1_w + sep_w + logo_slot + b2_w
        bx = center_x - total_inner_w // 2
        by = py1 + 9

        # Mini-logo CP2eJr + texto CP2eJr
        frame.alpha_composite(cp_mini, (bx, py1 + 4))
        draw.text((bx + logo_slot, by), badge_left, font=font_badge, fill=CP_ORANGE)

        # Separador
        draw.text((bx + logo_slot + b1_w, by), badge_sep, font=font_badge, fill=TEXT_MUTED)

        # Mini-logo MBY + texto Co-Founder @ Made By You
        mby_start_x = bx + logo_slot + b1_w + sep_w
        frame.alpha_composite(mby_mini, (mby_start_x, py1 + 4))
        draw.text((mby_start_x + logo_slot, by), badge_right, font=font_badge, fill=MBY_CYAN)

        # Converte para RGB sobre fundo exato #0d1117
        rgb_frame = frame.convert("RGB")
        frames.append(rgb_frame)

    print("Gerando folha de preview de frames...")
    # Salva uma folha com 6 frames chaves para inspeção visual
    sample_indices = [18, 55, 90, 118, 130, 150]
    sheet = Image.new("RGB", (WIDTH, HEIGHT * len(sample_indices)), BG_DARK)
    for idx, f_i in enumerate(sample_indices):
        sheet.paste(frames[f_i], (0, idx * HEIGHT))
    sheet.save(PREVIEW_PNG)

    print("Salvo preview em:", PREVIEW_PNG)

    # Salva WebP animado (qualidade máxima 24-bit)
    frames[0].save(
        OUTPUT_WEBP,
        save_all=True,
        append_images=frames[1:],
        duration=50,
        loop=0,
        lossless=False,
        quality=90
    )
    print("Salvo WebP animado em:", OUTPUT_WEBP)

    # Quantiza cada frame com FastOctree sem dither no fundo para preservar #0d1117 puro no GIF
    print("Otimizando paleta de cores e salvando GIF...")
    quantized_frames = [
        f.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
        for f in frames
    ]
    quantized_frames[0].save(
        OUTPUT_GIF,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=50,
        loop=0,
        optimize=False
    )
    print("Salvo GIF animado em:", OUTPUT_GIF)


if __name__ == "__main__":
    generate_banner()
