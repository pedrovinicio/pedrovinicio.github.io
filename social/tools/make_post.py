"""Mangue Games Instagram image generator (Fast Eleven, Carom Legends, Riot Racers, Gold Rush).

Usage: python3 make_post.py '<json spec>' out.jpg
A spec with "slides": [spec, ...] renders a carousel: out-1.jpg, out-2.jpg, ...

"game" (required): fast-eleven | carom-legends | riot-racers | gold-rush
  Sets the header (game icon + name) and the colour palette.

Layouts ("layout" key):
  hero      full-bleed art, headline at the bottom (default)
  stat      one giant number + label ("13" / "ligas para dominar")
  versus    question with two options side by side (A vs B poll)
  list      title + 3-5 numbered items (tips, facts, steps)
  card      solid colour block with a big headline, art strip at the bottom
  quote     tip / quote inside a framed card
theme: dark | color | light   ("green" = color and "yellow" = light, kept for Fast Eleven)
bg: an art file for the game, or a library image:
  fast-eleven   -> a game asset from fast-eleven/assets/images (FE_ASSETS), e.g. pitch-bg.png
  carom-legends -> icon.jpg                       (social/art/carom-legends/)
  riot-racers   -> icon.jpg, splash.jpg           (social/art/riot-racers/)
  gold-rush     -> icon.jpg, concept.jpg          (social/art/gold-rush/)
  "library/<game>/<file>" -> Pedro's photos/screenshots in social/library/<game>/ (see each README)
Common keys: bg, bg_y (0-1 vertical crop), bg_x (0-1 horizontal crop), kicker, theme, headline, highlight, sub;
plus number (stat), options [A, B] (versus), items [3-5] (list), footer (quote).
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1350
M = 80
SOCIAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FE_ASSETS = os.environ.get('FE_ASSETS', '/home/claude/fast-eleven/assets/images/')
FONTS = '/usr/share/fonts/opentype/inter/'


def palette(bg, fg, muted, accent, panel, light=False):
    return {'bg': bg, 'fg': fg, 'muted': muted, 'accent': accent, 'panel': panel, 'light': light}


GAMES = {
    'fast-eleven': {
        'name': 'FAST ELEVEN',
        'tip': 'Dica do técnico',
        'art': FE_ASSETS,
        'icon': 'icon.png',
        'defaults': {'hero': 'pitch-bg.png', 'stat': 'stadium-seats-bg.png', 'versus': 'home-hero.png',
                     'list': 'locker-bg.png', 'card': 'pitch-bg.png', 'quote': 'bench-bg.png'},
        'themes': {
            'dark': palette((13, 17, 23), '#FFFFFF', '#CDD5DE', '#FFD600', (22, 27, 34)),
            'color': palette((27, 94, 32), '#FFFFFF', '#DDEEDD', '#FFD600', (20, 70, 24)),
            'light': palette((255, 214, 0), '#0D1117', '#2A2F36', '#1B5E20', (240, 196, 0), True),
        },
    },
    'carom-legends': {
        'name': 'CAROM LEGENDS',
        'tip': 'Dica do mestre',
        'art': os.path.join(SOCIAL, 'art', 'carom-legends') + '/',
        'icon': 'icon.jpg',
        'defaults': {k: 'icon.jpg' for k in ('hero', 'stat', 'versus', 'list', 'card', 'quote')},
        'themes': {
            'dark': palette((11, 19, 38), '#FFFFFF', '#C9D3E6', '#F5C542', (20, 32, 60)),
            'color': palette((28, 86, 176), '#FFFFFF', '#DCE6F7', '#F5C542', (22, 68, 140)),
            'light': palette((245, 197, 66), '#0B1326', '#26314A', '#1C56B0', (232, 182, 50), True),
        },
    },
    'riot-racers': {
        'name': 'RIOT RACERS',
        'tip': 'Dica do piloto',
        'art': os.path.join(SOCIAL, 'art', 'riot-racers') + '/',
        'icon': 'icon.jpg',
        'defaults': {'hero': 'icon.jpg', 'stat': 'splash.jpg', 'versus': 'splash.jpg',
                     'list': 'icon.jpg', 'card': 'icon.jpg', 'quote': 'splash.jpg'},
        'themes': {
            'dark': palette((14, 16, 34), '#FFFFFF', '#CFCFE6', '#FF3EA5', (26, 28, 54)),
            'color': palette((196, 30, 120), '#FFFFFF', '#FFD9EC', '#FFC93C', (160, 22, 98)),
            'light': palette((255, 201, 60), '#14102A', '#2E2846', '#C81E78', (240, 186, 44), True),
        },
    },
    'gold-rush': {
        'name': 'GOLD RUSH',
        'tip': 'Dica do atleta',
        'art': os.path.join(SOCIAL, 'art', 'gold-rush') + '/',
        'icon': 'icon.jpg',
        'defaults': {'hero': 'icon.jpg', 'stat': 'concept.jpg', 'versus': 'icon.jpg',
                     'list': 'concept.jpg', 'card': 'icon.jpg', 'quote': 'concept.jpg'},
        'themes': {
            'dark': palette((14, 22, 52), '#FFFFFF', '#CCD5EE', '#FFC531', (24, 34, 74)),
            'color': palette((22, 66, 168), '#FFFFFF', '#DCE5FA', '#FFC531', (18, 52, 134)),
            'light': palette((255, 197, 49), '#101A40', '#2A3560', '#C8102E', (240, 182, 36), True),
        },
    },
}
THEME_ALIASES = {'green': 'color', 'yellow': 'light'}
GAME = GAMES['fast-eleven']


def font(weight, size):
    return ImageFont.truetype(f'{FONTS}Inter-{weight}.otf', size)


def wrap(d, text, f, maxw):
    lines, cur = [], ''
    for word in text.split():
        trial = (cur + ' ' + word).strip()
        if d.textlength(trial, font=f) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return [l for l in lines if l]


def fit_font(d, text, weight, start, maxw, max_lines):
    size = start
    while size > 40:
        f = font(weight, size)
        if len(wrap(d, text, f, maxw)) <= max_lines:
            return f
        size -= 4
    return font(weight, size)


def art(name, w, h, y=0.5, blur=0, x=0.5):
    path = os.path.join(SOCIAL, name) if name.startswith('library/') else GAME['art'] + name
    im = Image.open(path).convert('RGB')
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1))
    ox = int((im.width - w) * x)
    oy = int((im.height - h) * y)
    im = im.crop((ox, oy, ox + w, oy + h))
    return im.filter(ImageFilter.GaussianBlur(blur)) if blur else im


def darken(im, color, start=0.35, strength=235, top=0):
    w, h = im.size
    mask = Image.new('L', (1, h))
    for y in range(h):
        t = y / h
        v = strength * max(0, (t - start) / (1 - start)) ** 0.9
        if top:
            v = max(v, top * max(0, 1 - t / 0.25))
        mask.putpixel((0, y), int(min(255, v)))
    return Image.composite(Image.new('RGB', (w, h), color), im, mask.resize((w, h)))


def brand(im, d, th, kicker, x=M, y=M):
    ic = Image.open(GAME['art'] + GAME['icon']).convert('RGBA').resize((96, 96))
    mask = Image.new('L', (96, 96), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 96, 96), 22, fill=255)
    im.paste(ic, (x, y), mask)
    d.text((x + 118, y + 14), GAME['name'], font=font('Black', 36), fill=th['fg'])
    if kicker:
        d.text((x + 118, y + 58), kicker.upper(), font=font('SemiBold', 22), fill=th['accent'])


def headline(d, th, text, hi, f, x, y, maxw, align='left', lh=1.05):
    words = text.split()
    hw = hi.lower().split() if hi else []
    marked = [False] * len(words)
    for i in range(len(words) - len(hw) + 1):
        if hw and [w.lower().strip('.,!?:;') for w in words[i:i + len(hw)]] == [h.strip('.,!?:;') for h in hw]:
            for j in range(i, i + len(hw)):
                marked[j] = True
    space = d.textlength(' ', font=f)
    idx = 0
    for line in wrap(d, text, f, maxw):
        n = len(line.split())
        lx = x if align == 'left' else x + (maxw - d.textlength(line, font=f)) / 2
        for w, m in zip(words[idx:idx + n], marked[idx:idx + n]):
            d.text((lx, y), w, font=f, fill=th['accent'] if m else th['fg'])
            lx += d.textlength(w, font=f) + space
        idx += n
        y += int(f.size * lh)
    return y


def para(d, color, text, f, x, y, maxw, align='left'):
    for line in wrap(d, text, f, maxw):
        lx = x if align == 'left' else x + (maxw - d.textlength(line, font=f)) / 2
        d.text((lx, y), line, font=f, fill=color)
        y += int(f.size * 1.35)
    return y


def block_height(d, text, f, maxw, lh):
    return len(wrap(d, text, f, maxw)) * int(f.size * lh) if text else 0


def layout_hero(s, th):
    im = darken(art(BG(s), W, H, s.get('bg_y', 0.5), x=s.get('bg_x', 0.5)), th['bg'], top=150)
    d = ImageDraw.Draw(im)
    brand(im, d, th, s.get('kicker'))
    hf = fit_font(d, s['headline'], 'Black', s.get('hsize', 96), W - 2 * M, 4)
    sf = font('Medium', 40)
    y = H - M - block_height(d, s.get('sub'), sf, W - 2 * M, 1.35) - (30 if s.get('sub') else 0)
    y -= block_height(d, s['headline'], hf, W - 2 * M, 1.05)
    d.rectangle((M, y - 36, M + 90, y - 26), fill=th['accent'])
    y = headline(d, th, s['headline'], s.get('highlight'), hf, M, y, W - 2 * M)
    if s.get('sub'):
        para(d, th['muted'], s['sub'], sf, M, y + 30, W - 2 * M)
    return im


def layout_stat(s, th):
    im = Image.new('RGB', (W, H), th['bg'])
    strip = darken(art(BG(s), W, 520, s.get('bg_y', 0.5), x=s.get('bg_x', 0.5)), th['bg'], start=0.0, strength=160)
    fade = Image.new('L', (1, 520))
    for y in range(520):
        fade.putpixel((0, y), int(255 * min(1, (520 - y) / 260)))
    im.paste(strip, (0, H - 520), fade.resize((W, 520)).transpose(Image.FLIP_TOP_BOTTOM))
    d = ImageDraw.Draw(im)
    brand(im, d, th, s.get('kicker'))
    num = str(s['number'])
    nf = font('Black', 420 if len(num) <= 2 else 300)
    bbox = d.textbbox((0, 0), num, font=nf)
    d.text((M - bbox[0], 240 - bbox[1]), num, font=nf, fill=th['accent'])
    y = 240 + (bbox[3] - bbox[1]) + 50
    hf = fit_font(d, s['headline'], 'Black', 84, W - 2 * M, 3)
    y = headline(d, th, s['headline'], s.get('highlight'), hf, M, y, W - 2 * M)
    if s.get('sub'):
        para(d, th['muted'], s['sub'], font('Medium', 38), M, y + 24, W - 2 * M)
    return im


def layout_versus(s, th):
    im = darken(art(BG(s), W, H, s.get('bg_y', 0.5), x=s.get('bg_x', 0.5), blur=6), th['bg'], start=0.0, strength=190)
    d = ImageDraw.Draw(im)
    brand(im, d, th, s.get('kicker', 'Sua vez'))
    hf = fit_font(d, s['headline'], 'Black', 88, W - 2 * M, 3)
    y = headline(d, th, s['headline'], s.get('highlight'), hf, M, 280, W - 2 * M, align='center')
    a, b = s['options'][:2]
    top = max(y + 70, 640)
    cw, ch, gap = (W - 2 * M - 40) // 2, 400, 40
    for i, (label, txt) in enumerate((('A', a), ('B', b))):
        x = M + i * (cw + gap)
        d.rounded_rectangle((x, top, x + cw, top + ch), 36, fill=th['panel'], outline=th['accent'], width=4)
        d.text((x + 36, top + 30), label, font=font('Black', 64), fill=th['accent'])
        of = fit_font(d, txt, 'Black', 64, cw - 72, 3)
        oy = top + ch - 40 - block_height(d, txt, of, cw - 72, 1.05)
        headline(d, th, txt, None, of, x + 36, oy, cw - 72)
    vf = font('Black', 44)
    cx, cy = W // 2, top + ch // 2
    d.ellipse((cx - 50, cy - 50, cx + 50, cy + 50), fill=th['accent'])
    tw = d.textlength('VS', font=vf)
    d.text((cx - tw / 2, cy - 27), 'VS', font=vf, fill=th['bg'] if not th['light'] else '#FFFFFF')
    para(d, th['muted'], s.get('sub', 'Vota nos comentários!'), font('SemiBold', 38), M, top + ch + 60, W - 2 * M, align='center')
    return im


def layout_list(s, th):
    im = Image.new('RGB', (W, H), th['bg'])
    d = ImageDraw.Draw(im)
    side = art(BG(s), 300, H, s.get('bg_y', 0.5), x=s.get('bg_x', 0.5))
    side = darken(side, th['bg'], start=0.0, strength=120)
    im.paste(side, (W - 300, 0))
    fade = Image.new('L', (300, 1))
    for x in range(300):
        fade.putpixel((x, 0), int(255 * max(0, 1 - x / 300)))
    im.paste(Image.new('RGB', (300, H), th['bg']), (W - 300, 0), fade.resize((300, H)))
    brand(im, d, th, s.get('kicker'))
    maxw = W - 2 * M - 120
    hf = fit_font(d, s['headline'], 'Black', 80, maxw, 3)
    y = headline(d, th, s['headline'], s.get('highlight'), hf, M, 250, maxw) + 50
    items = s['items'][:5]
    itf = font('Bold', 44 if len(items) <= 3 else 38)
    for i, item in enumerate(items, 1):
        d.rounded_rectangle((M, y, M + 76, y + 76), 18, fill=th['accent'])
        nf = font('Black', 44)
        tw = d.textlength(str(i), font=nf)
        d.text((M + 38 - tw / 2, y + 12), str(i), font=nf, fill=th['bg'] if not th['light'] else '#FFFFFF')
        end = para(d, th['fg'], item, itf, M + 108, y + 10, maxw - 108)
        y = max(end, y + 76) + 34
    return im


def layout_card(s, th):
    im = Image.new('RGB', (W, H), th['bg'])
    ah = 520
    strip = art(BG(s), W - 2 * 50, ah, s.get('bg_y', 0.5), x=s.get('bg_x', 0.5))
    mask = Image.new('L', strip.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *strip.size), 40, fill=255)
    im.paste(strip, (50, H - ah - 50), mask)
    d = ImageDraw.Draw(im)
    brand(im, d, th, s.get('kicker'))
    hf = fit_font(d, s['headline'], 'Black', 104, W - 2 * M, 4)
    y = headline(d, th, s['headline'], s.get('highlight'), hf, M, 250, W - 2 * M)
    if s.get('sub'):
        para(d, th['muted'], s['sub'], font('Medium', 38), M, y + 24, W - 2 * M)
    return im


def layout_quote(s, th):
    im = darken(art(BG(s), W, H, s.get('bg_y', 0.5), x=s.get('bg_x', 0.5), blur=10), th['bg'], start=0.0, strength=170)
    d = ImageDraw.Draw(im)
    brand(im, d, th, s.get('kicker', GAME['tip']))
    inner = W - 2 * M - 100
    hf = fit_font(d, s['headline'], 'Black', 84, inner, 5)
    sf = font('Medium', 40)
    total = block_height(d, s['headline'], hf, inner, 1.08)
    if s.get('sub'):
        total += 30 + block_height(d, s['sub'], sf, inner, 1.35)
    box_h = total + 260
    top = (H - box_h) // 2 + 40
    d.rounded_rectangle((M, top, W - M, top + box_h), 44, fill=th['panel'], outline=th['accent'], width=3)
    d.text((M + 50, top - 10), '“', font=font('Black', 220), fill=th['accent'])
    y = headline(d, th, s['headline'], s.get('highlight'), hf, M + 50, top + 170, inner, lh=1.08)
    if s.get('sub'):
        para(d, th['muted'], s['sub'], sf, M + 50, y + 30, inner)
    if s.get('footer'):
        para(d, th['accent'], s['footer'], font('Bold', 32), M, top + box_h + 50, W - 2 * M, align='center')
    return im


LAYOUTS = {
    'hero': layout_hero,
    'stat': layout_stat,
    'versus': layout_versus,
    'list': layout_list,
    'card': layout_card,
    'quote': layout_quote,
}


def BG(s):
    return s.get('bg') or GAME['defaults'][s.get('layout', 'hero')]


def make(spec, out):
    global GAME
    if spec.get('game') not in GAMES:
        sys.exit(f"spec needs \"game\": one of {', '.join(GAMES)}")
    GAME = GAMES[spec['game']]
    theme = THEME_ALIASES.get(spec.get('theme', 'dark'), spec.get('theme', 'dark'))
    th = GAME['themes'][theme]
    LAYOUTS[spec.get('layout', 'hero')](spec, th).save(out, quality=92)


def main():
    spec, out = json.loads(sys.argv[1]), sys.argv[2]
    if 'slides' in spec:
        base, ext = os.path.splitext(out)
        for i, slide in enumerate(spec['slides'], 1):
            merged = {k: v for k, v in spec.items() if k != 'slides'}
            merged.update(slide)
            make(merged, f'{base}-{i}{ext}')
    else:
        make(spec, out)


if __name__ == '__main__':
    main()
