#!/usr/bin/env python3
"""
Mahavir Ka Vandan — Devotional Video Generator
Creates a short video from the devotional poem about Bhagwan Mahavir.
"""

import os
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

# Video settings
WIDTH, HEIGHT = 1280, 720
FPS = 25
SLIDE_DURATION = 6      # seconds per verse slide
TITLE_DURATION = 5      # seconds for title
FADE_DURATION = 1       # seconds for fade
TRANSITION_FRAMES = int(FADE_DURATION * FPS)
SLIDE_FRAMES = int(SLIDE_DURATION * FPS)
TITLE_FRAMES = int(TITLE_DURATION * FPS)

OUTPUT_DIR = "/home/user/awesome/video_frames"
OUTPUT_VIDEO = "/home/user/awesome/mahavir_vandan.mp4"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color palette — Jain saffron & gold theme
BG_TOP    = (120, 40, 10)    # deep saffron-brown
BG_BOT    = (40, 10, 5)      # dark maroon
GOLD      = (255, 210, 80)
CREAM     = (255, 245, 220)
ORANGE    = (255, 140, 30)
WHITE     = (255, 255, 255)
SOFT_GOLD = (230, 185, 60)

# ── font helpers ──────────────────────────────────────────────────────────────
def load_font(size, bold=False):
    """Try common system fonts, fall back to default."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

# ── gradient background ───────────────────────────────────────────────────────
def make_bg():
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(BG_TOP[0] * (1 - t) + BG_BOT[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOT[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOT[2] * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return img

# ── decorative border ─────────────────────────────────────────────────────────
def draw_border(draw):
    m = 18
    draw.rectangle([m, m, WIDTH - m, HEIGHT - m],
                   outline=GOLD, width=3)
    draw.rectangle([m + 8, m + 8, WIDTH - m - 8, HEIGHT - m - 8],
                   outline=SOFT_GOLD, width=1)
    # corner flourishes
    sz = 20
    for cx, cy in [(m, m), (WIDTH - m, m), (m, HEIGHT - m), (WIDTH - m, HEIGHT - m)]:
        draw.ellipse([cx - sz//2, cy - sz//2, cx + sz//2, cy + sz//2],
                     outline=GOLD, width=2)

# ── Om / Jain symbol (drawn with circles & lines) ────────────────────────────
def draw_jain_symbol(draw, cx, cy, r=22):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=2)
    draw.ellipse([cx - r//2, cy - r//2, cx + r//2, cy + r//2],
                 outline=SOFT_GOLD, width=1)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=GOLD, width=1)
    draw.line([(cx, cy - r), (cx, cy + r)], fill=GOLD, width=1)

# ── text wrapping ─────────────────────────────────────────────────────────────
def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        w = draw.textlength(test, font=font)
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

# ── render a slide ────────────────────────────────────────────────────────────
def render_slide(title_line1, title_line2, body_lines, refrain=None,
                 show_author=False):
    bg = make_bg()
    draw = ImageDraw.Draw(bg)
    draw_border(draw)

    # Decorative symbols
    for sx in [60, WIDTH // 2, WIDTH - 60]:
        draw_jain_symbol(draw, sx, 34)
    for sx in [60, WIDTH // 2, WIDTH - 60]:
        draw_jain_symbol(draw, sx, HEIGHT - 34)

    font_title  = load_font(38, bold=True)
    font_verse  = load_font(26)
    font_refrain = load_font(23)
    font_small  = load_font(18)
    font_tiny   = load_font(15)

    y = 70

    # Title lines
    if title_line1:
        t1_w = draw.textlength(title_line1, font=font_title)
        draw.text(((WIDTH - t1_w) / 2, y), title_line1, font=font_title, fill=GOLD)
        y += 50
    if title_line2:
        t2_w = draw.textlength(title_line2, font=font_title)
        draw.text(((WIDTH - t2_w) / 2, y), title_line2, font=font_title, fill=ORANGE)
        y += 50

    # Divider
    draw.line([(100, y + 5), (WIDTH - 100, y + 5)], fill=GOLD, width=1)
    y += 22

    # Body text
    max_w = WIDTH - 160
    for line in body_lines:
        if not line.strip():
            y += 14
            continue
        wrapped = wrap_text(line, font_verse, max_w, draw)
        for wl in wrapped:
            wl_w = draw.textlength(wl, font=font_verse)
            draw.text(((WIDTH - wl_w) / 2, y), wl, font=font_verse, fill=CREAM)
            y += 36

    if refrain:
        y += 8
        draw.line([(120, y), (WIDTH - 120, y)], fill=SOFT_GOLD, width=1)
        y += 14
        rw = draw.textlength(refrain, font=font_refrain)
        draw.text(((WIDTH - rw) / 2, y), refrain, font=font_refrain, fill=ORANGE)
        y += 36

    if show_author:
        y += 10
        draw.line([(100, y), (WIDTH - 100, y)], fill=GOLD, width=1)
        y += 14
        author_lines = [
            "Composed by Arthika Gyanmati Mataji",
            "On the occasion of her 68th birth anniversary — 1 November 2001",
        ]
        for al in author_lines:
            aw = draw.textlength(al, font=font_tiny)
            draw.text(((WIDTH - aw) / 2, y), al, font=font_tiny, fill=SOFT_GOLD)
            y += 22

    return bg


# ── slide definitions ─────────────────────────────────────────────────────────
REFRAIN = "— O Siddharth's son!"

SLIDES = [
    # (title_line1, title_line2, body_lines, refrain, show_author, duration_frames)
    (
        "Mahavir Ka Vandan",
        "Salutation to Mahavir",
        [
            "A devotional poem — Bhagwan Shri 1008 Mahavir Swami",
            "2600th Birth Anniversary · 21 June 2009",
        ],
        None, False, TITLE_FRAMES,
    ),
    (
        "Verse 1", "",
        [
            "O son of Siddharth, you taught us the true way to live,",
            "Son of Trishala, you showed us what it means to be human.",
            "When restlessness had spread across the earth,",
            "The ocean of non-violence poured forth the nectar of compassion.",
            "The great abode of Nandan, you made your very own —",
        ],
        REFRAIN, False, SLIDE_FRAMES,
    ),
    (
        "Verse 2", "",
        [
            "When society had lost its way, you alone understood,",
            "You sounded the bugle of the law of karma.",
            "O young Vardhamana, you erased the illusion",
            "of worldly attachment —",
        ],
        REFRAIN, False, SLIDE_FRAMES,
    ),
    (
        "Verse 3", "",
        [
            "When the spirit of hoarding gripped the world,",
            "You showed the path of non-possession, uniting all in simplicity.",
            "The renunciant showed everyone the way of contentment —",
        ],
        REFRAIN, False, SLIDE_FRAMES,
    ),
    (
        "Verse 4", "",
        [
            "When debaters and disputants spread chaos,",
            "You coloured them in the hues of Syadvad",
            "(the doctrine of many perspectives).",
            "Through deep penance, becoming like sandalwood,",
            "you taught by example —",
        ],
        REFRAIN, False, SLIDE_FRAMES,
    ),
    (
        "Verse 5", "",
        [
            "When aggressors came time and again, raiding home after home,",
            "You taught everyone to walk the path of self-restraint.",
            "The brave of soul made even the fearful into warriors —",
        ],
        REFRAIN, False, SLIDE_FRAMES,
    ),
    (
        "Verse 6", "",
        [
            "When transformation and destruction were about to take hold,",
            "The lamp of dharma was flickering — you saved its light.",
            "Mahavir gave the whole world a refuge",
            "from worldly temptation —",
        ],
        REFRAIN, True, SLIDE_FRAMES,
    ),
]

# ── fade helpers ──────────────────────────────────────────────────────────────
def apply_fade(img, alpha):
    """alpha: 0=black, 1=full"""
    if alpha >= 1.0:
        return img
    black = Image.new("RGB", img.size, (0, 0, 0))
    return Image.blend(black, img, alpha)


# ── main render loop ──────────────────────────────────────────────────────────
frame_idx = 0

def save_frame(img):
    global frame_idx
    img.save(os.path.join(OUTPUT_DIR, f"frame_{frame_idx:06d}.png"))
    frame_idx += 1

rendered = [render_slide(*s[:5]) for s in SLIDES]

print(f"Generating {len(SLIDES)} slides …")

for si, (slide_img, slide_data) in enumerate(zip(rendered, SLIDES)):
    duration = slide_data[5]

    # fade-in
    for fi in range(TRANSITION_FRAMES):
        alpha = fi / TRANSITION_FRAMES
        save_frame(apply_fade(slide_img, alpha))

    # hold
    hold = duration - 2 * TRANSITION_FRAMES
    for _ in range(max(hold, 0)):
        save_frame(slide_img.copy())

    # fade-out (to next slide via black)
    for fi in range(TRANSITION_FRAMES):
        alpha = 1.0 - fi / TRANSITION_FRAMES
        save_frame(apply_fade(slide_img, alpha))

total_frames = frame_idx
print(f"Total frames generated: {total_frames}  (~{total_frames/FPS:.1f} s)")

# ── assemble video with ffmpeg ────────────────────────────────────────────────
print("Assembling video …")
cmd = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(OUTPUT_DIR, "frame_%06d.png"),
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "22",
    "-pix_fmt", "yuv420p",
    OUTPUT_VIDEO,
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("ffmpeg error:", result.stderr[-500:])
else:
    size_mb = os.path.getsize(OUTPUT_VIDEO) / 1_048_576
    print(f"Video saved: {OUTPUT_VIDEO}  ({size_mb:.1f} MB)")
