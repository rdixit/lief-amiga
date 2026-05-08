#!/usr/bin/env python3
"""
AMIGA-AAC Symbol SVG Generator
================================
Generates symbols.js - a complete set of pictographic SVG icons for every
vocabulary word in vocabulary.json.

Style guide:
- viewBox="0 0 100 100", no background (card CSS handles that)
- Friendly, clean pictographic style - between geometric and illustrative
- Bold, recognizable at 60-80px rendered size
- Category-aware color palette
- Expressive faces and clear silhouettes

Run: python3 generate_symbols.py
Output: symbols.js (import as ES module in app.js)
"""

import json
import os

# ─── COLOR PALETTE ────────────────────────────────────────────────────────────
# Category colors
C_AMBER   = "#f59e0b"   # pronouns / people
C_AMBER_L = "#fcd34d"   # light amber
C_AMBER_D = "#b45309"   # dark amber
C_GREEN   = "#10b981"   # actions / verbs
C_GREEN_L = "#6ee7b7"
C_GREEN_D = "#065f46"
C_BLUE    = "#3b82f6"   # things / places
C_BLUE_L  = "#93c5fd"
C_BLUE_D  = "#1e40af"
C_ROSE    = "#f43f5e"   # stop / negation
C_PINK    = "#ec4899"   # social / please
C_PINK_L  = "#f9a8d4"
C_PURPLE  = "#8b5cf6"   # play / more
C_PURPLE_L= "#c4b5fd"
C_ORANGE  = "#f97316"   # food / warmth
C_ORANGE_L= "#fed7aa"
C_YELLOW  = "#fbbf24"   # happy / feelings
C_YELLOW_L= "#fef3c7"
C_TEAL    = "#14b8a6"   # water / calm
C_TEAL_L  = "#99f6e4"
C_GRAY    = "#6b7280"
C_GRAY_L  = "#e5e7eb"
C_RED     = "#ef4444"
C_SKIN    = "#fde8d0"   # face skin
C_SKIN_D  = "#f5c5a3"   # darker skin
C_DARK    = "#1f2937"   # outlines / pupils
C_WHITE   = "#ffffff"

def face(cx, cy, r, skin=C_SKIN, eye_color=C_DARK, mouth_type="smile", blush=False):
    """Generate a simple expressive face SVG fragment."""
    parts = []
    # Head
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{skin}"/>')
    # Eyes
    ex = r * 0.3
    ey = r * 0.25
    er = r * 0.1
    parts.append(f'<circle cx="{cx-ex}" cy="{cy-ey}" r="{er}" fill="{eye_color}"/>')
    parts.append(f'<circle cx="{cx+ex}" cy="{cy-ey}" r="{er}" fill="{eye_color}"/>')
    # Eye shine
    parts.append(f'<circle cx="{cx-ex+er*0.4}" cy="{cy-ey-er*0.3}" r="{er*0.35}" fill="white" opacity="0.8"/>')
    parts.append(f'<circle cx="{cx+ex+er*0.4}" cy="{cy-ey-er*0.3}" r="{er*0.35}" fill="white" opacity="0.8"/>')
    # Mouth
    my = cy + r * 0.2
    mw = r * 0.35
    if mouth_type == "smile":
        parts.append(f'<path d="M{cx-mw},{my} Q{cx},{my+r*0.22} {cx+mw},{my}" stroke="{eye_color}" stroke-width="{r*0.1:.1f}" fill="none" stroke-linecap="round"/>')
    elif mouth_type == "grin":
        parts.append(f'<path d="M{cx-mw},{my} Q{cx},{my+r*0.3} {cx+mw},{my}" stroke="{eye_color}" stroke-width="{r*0.1:.1f}" fill="none" stroke-linecap="round"/>')
    elif mouth_type == "frown":
        parts.append(f'<path d="M{cx-mw},{my+r*0.15} Q{cx},{my-r*0.1} {cx+mw},{my+r*0.15}" stroke="{eye_color}" stroke-width="{r*0.1:.1f}" fill="none" stroke-linecap="round"/>')
    elif mouth_type == "neutral":
        parts.append(f'<line x1="{cx-mw}" y1="{my+r*0.05}" x2="{cx+mw}" y2="{my+r*0.05}" stroke="{eye_color}" stroke-width="{r*0.09:.1f}" stroke-linecap="round"/>')
    elif mouth_type == "open_smile":
        parts.append(f'<path d="M{cx-mw},{my} Q{cx},{my+r*0.35} {cx+mw},{my}" stroke="{eye_color}" stroke-width="{r*0.08:.1f}" fill="{C_ROSE}" opacity="0.7"/>')
    # Blush
    if blush:
        br = r * 0.15
        parts.append(f'<circle cx="{cx-ex*1.3}" cy="{cy+r*0.05}" r="{br}" fill="#f472b6" opacity="0.35"/>')
        parts.append(f'<circle cx="{cx+ex*1.3}" cy="{cy+r*0.05}" r="{br}" fill="#f472b6" opacity="0.35"/>')
    return "\n".join(parts)

def body(cx, cy_top, w, h, color, has_neck=True):
    """Simple torso/body block."""
    bw = w * 0.5
    if has_neck:
        nw = w * 0.08
        return f'<rect x="{cx-bw/2}" y="{cy_top}" width="{bw}" height="{h}" rx="{w*0.08}" fill="{color}"/>'
    return f'<rect x="{cx-bw/2}" y="{cy_top}" width="{bw}" height="{h}" rx="{w*0.08}" fill="{color}"/>'

def person(cx, cy, scale=1.0, shirt=C_AMBER, hair=None, skirt=False, caption=None):
    """Full standing person figure."""
    r = 10 * scale
    parts = []
    # Hair
    if hair:
        parts.append(f'<ellipse cx="{cx}" cy="{cy-r*0.7}" rx="{r*1.1}" ry="{r*0.65}" fill="{hair}"/>')
    # Head
    parts.append(face(cx, cy, r, blush=False))
    # Neck
    ny = cy + r
    nh = r * 0.6
    parts.append(f'<rect x="{cx-r*0.2}" y="{ny}" width="{r*0.4}" height="{nh}" fill="{C_SKIN_D}"/>')
    # Body
    by_top = ny + nh
    bh = r * 2.2
    bw = r * 2.2
    parts.append(f'<rect x="{cx-bw/2}" y="{by_top}" width="{bw}" height="{bh}" rx="{r*0.35}" fill="{shirt}"/>')
    # Arms
    arm_y = by_top + bh * 0.2
    parts.append(f'<line x1="{cx-bw/2}" y1="{arm_y}" x2="{cx-bw/2-r*1.0}" y2="{arm_y+bh*0.5}" stroke="{shirt}" stroke-width="{r*0.6:.1f}" stroke-linecap="round"/>')
    parts.append(f'<line x1="{cx+bw/2}" y1="{arm_y}" x2="{cx+bw/2+r*1.0}" y2="{arm_y+bh*0.5}" stroke="{shirt}" stroke-width="{r*0.6:.1f}" stroke-linecap="round"/>')
    # Legs
    leg_y = by_top + bh
    if skirt:
        parts.append(f'<path d="M{cx-bw/2},{leg_y-bh*0.1} Q{cx},{leg_y+bh*0.5} {cx+bw/2},{leg_y-bh*0.1}" fill="{C_PINK_L}"/>')
    parts.append(f'<line x1="{cx-bw*0.25}" y1="{leg_y}" x2="{cx-bw*0.3}" y2="{leg_y+bh*0.9}" stroke=C_GRAY stroke-width="{r*0.55:.1f}" stroke-linecap="round"/>'.replace("C_GRAY", f'"{C_GRAY}"'))
    parts.append(f'<line x1="{cx+bw*0.25}" y1="{leg_y}" x2="{cx+bw*0.3}" y2="{leg_y+bh*0.9}" stroke=C_GRAY stroke-width="{r*0.55:.1f}" stroke-linecap="round"/>'.replace("C_GRAY", f'"{C_GRAY}"'))
    return "\n".join(parts)

def svg(content, extra_defs=""):
    return f'<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">{extra_defs}{content}</svg>'

# ─── SVG DEFINITIONS ──────────────────────────────────────────────────────────
# Each entry: "symbol_id": "<svg>...</svg>"
# All SVGs: viewBox="0 0 100 100", no background fill

SVGS = {}

# ════════════════════════════════════════════════════════════════
# PEOPLE / PRONOUNS
# ════════════════════════════════════════════════════════════════

SVGS["i"] = svg(f"""
  {face(50, 28, 14)}
  <rect x="39" y="44" width="22" height="26" rx="5" fill="{C_AMBER}"/>
  <line x1="39" y1="50" x2="25" y2="62" stroke="{C_AMBER}" stroke-width="7" stroke-linecap="round"/>
  <line x1="61" y1="50" x2="75" y2="62" stroke="{C_AMBER}" stroke-width="7" stroke-linecap="round"/>
  <line x1="42" y1="70" x2="40" y2="88" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <line x1="58" y1="70" x2="60" y2="88" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <circle cx="50" cy="93" r="4" fill="{C_AMBER}" opacity="0.6"/>
  <text x="50" y="98" text-anchor="middle" font-size="6" fill="{C_AMBER}" font-weight="bold" opacity="0.5">ME</text>
""")

SVGS["you"] = svg(f"""
  {face(50, 28, 14)}
  <rect x="39" y="44" width="22" height="26" rx="5" fill="{C_AMBER}"/>
  <line x1="39" y1="50" x2="22" y2="58" stroke="{C_AMBER}" stroke-width="7" stroke-linecap="round"/>
  <line x1="61" y1="50" x2="78" y2="58" stroke="{C_AMBER}" stroke-width="7" stroke-linecap="round"/>
  <line x1="42" y1="70" x2="40" y2="88" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <line x1="58" y1="70" x2="60" y2="88" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <path d="M72 72 L85 72 M78 66 L85 72 L78 78" stroke="{C_AMBER_D}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
""")

SVGS["me"] = svg(f"""
  {face(50, 30, 14)}
  <rect x="39" y="46" width="22" height="24" rx="5" fill="{C_AMBER}"/>
  <line x1="39" y1="52" x2="26" y2="64" stroke="{C_AMBER}" stroke-width="7" stroke-linecap="round"/>
  <line x1="61" y1="52" x2="74" y2="64" stroke="{C_AMBER}" stroke-width="7" stroke-linecap="round"/>
  <line x1="42" y1="70" x2="40" y2="86" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <line x1="58" y1="70" x2="60" y2="86" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <path d="M26 79 Q26 90 36 90" stroke="{C_AMBER_D}" stroke-width="3.5" fill="none" stroke-linecap="round"/>
  <circle cx="36" cy="90" r="3" fill="{C_AMBER_D}"/>
""")

SVGS["my"] = svg(f"""
  {face(42, 28, 12)}
  <rect x="33" y="42" width="18" height="20" rx="4" fill="{C_AMBER}"/>
  <line x1="33" y1="47" x2="22" y2="56" stroke="{C_AMBER}" stroke-width="6" stroke-linecap="round"/>
  <line x1="51" y1="47" x2="62" y2="56" stroke="{C_AMBER}" stroke-width="6" stroke-linecap="round"/>
  <line x1="36" y1="62" x2="35" y2="76" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="48" y1="62" x2="49" y2="76" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <rect x="60" y="50" width="26" height="22" rx="4" fill="{C_AMBER_L}" stroke="{C_AMBER}" stroke-width="2"/>
  <path d="M62 52 L73 60 L84 52" stroke="{C_AMBER_D}" stroke-width="2" fill="none"/>
""")

SVGS["we"] = svg(f"""
  {face(32, 28, 11)}
  <rect x="23" y="41" width="18" height="20" rx="4" fill="{C_AMBER}"/>
  <line x1="23" y1="46" x2="13" y2="55" stroke="{C_AMBER}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="41" y1="46" x2="51" y2="55" stroke="{C_AMBER}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="26" y1="61" x2="25" y2="75" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="38" y1="61" x2="39" y2="75" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  {face(68, 28, 11)}
  <rect x="59" y="41" width="18" height="20" rx="4" fill="{C_ORANGE}"/>
  <line x1="59" y1="46" x2="49" y2="55" stroke="{C_ORANGE}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="77" y1="46" x2="87" y2="55" stroke="{C_ORANGE}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="62" y1="61" x2="61" y2="75" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="74" y1="61" x2="75" y2="75" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <path d="M46 52 L54 52" stroke="{C_AMBER_D}" stroke-width="3" stroke-linecap="round"/>
""")

SVGS["he"] = svg(f"""
  {face(50, 28, 14, skin=C_SKIN)}
  <rect x="39" y="44" width="22" height="26" rx="5" fill="{C_BLUE}"/>
  <line x1="39" y1="50" x2="24" y2="60" stroke="{C_BLUE}" stroke-width="7" stroke-linecap="round"/>
  <line x1="61" y1="50" x2="76" y2="60" stroke="{C_BLUE}" stroke-width="7" stroke-linecap="round"/>
  <line x1="42" y1="70" x2="40" y2="88" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <line x1="58" y1="70" x2="60" y2="88" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <rect x="36" y="18" width="28" height="8" rx="4" fill="{C_BLUE_D}"/>
""")

SVGS["she"] = svg(f"""
  {face(50, 28, 14, skin=C_SKIN)}
  <rect x="39" y="44" width="22" height="26" rx="5" fill="{C_PINK}"/>
  <line x1="39" y1="50" x2="24" y2="60" stroke="{C_PINK}" stroke-width="7" stroke-linecap="round"/>
  <line x1="61" y1="50" x2="76" y2="60" stroke="{C_PINK}" stroke-width="7" stroke-linecap="round"/>
  <line x1="42" y1="70" x2="40" y2="88" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <line x1="58" y1="70" x2="60" y2="88" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <path d="M36 18 Q50 10 64 18" stroke="{C_PINK}" stroke-width="4" fill="none" stroke-linecap="round"/>
""")

SVGS["he_she"] = svg(f"""
  {face(30, 30, 11, skin=C_SKIN)}
  <rect x="22" y="43" width="16" height="20" rx="4" fill="{C_BLUE}"/>
  <line x1="22" y1="48" x2="12" y2="56" stroke="{C_BLUE}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="38" y1="48" x2="44" y2="56" stroke="{C_BLUE}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="25" y1="63" x2="24" y2="78" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="35" y1="63" x2="36" y2="78" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <rect x="24" y="20" width="14" height="5" rx="2.5" fill="{C_BLUE_D}"/>
  {face(70, 30, 11, skin=C_SKIN)}
  <rect x="62" y="43" width="16" height="20" rx="4" fill="{C_PINK}"/>
  <line x1="62" y1="48" x2="56" y2="56" stroke="{C_PINK}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="78" y1="48" x2="88" y2="56" stroke="{C_PINK}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="65" y1="63" x2="64" y2="78" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="75" y1="63" x2="76" y2="78" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <path d="M64 20 Q70 14 76 20" stroke="{C_PINK}" stroke-width="3" fill="none" stroke-linecap="round"/>
""")

SVGS["mine"] = svg(f"""
  {face(42, 25, 12)}
  <rect x="33" y="39" width="18" height="20" rx="4" fill="{C_AMBER}"/>
  <line x1="33" y1="44" x2="22" y2="53" stroke="{C_AMBER}" stroke-width="6" stroke-linecap="round"/>
  <line x1="51" y1="44" x2="68" y2="62" stroke="{C_AMBER}" stroke-width="6" stroke-linecap="round"/>
  <line x1="36" y1="59" x2="35" y2="73" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="48" y1="59" x2="49" y2="73" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <circle cx="74" cy="68" r="12" fill="{C_YELLOW}" stroke="{C_AMBER}" stroke-width="2.5"/>
  <path d="M69 68 L73 72 L80 64" stroke="{C_AMBER_D}" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
""")

SVGS["mom"] = svg(f"""
  <ellipse cx="50" cy="20" rx="15" ry="9" fill="{C_AMBER_D}"/>
  {face(50, 29, 13, blush=True)}
  <rect x="38" y="44" width="24" height="26" rx="5" fill="{C_PINK}"/>
  <line x1="38" y1="50" x2="24" y2="62" stroke="{C_PINK}" stroke-width="7" stroke-linecap="round"/>
  <line x1="62" y1="50" x2="76" y2="62" stroke="{C_PINK}" stroke-width="7" stroke-linecap="round"/>
  <line x1="44" y1="70" x2="43" y2="88" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <line x1="56" y1="70" x2="57" y2="88" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <path d="M43 70 Q50 80 57 70" fill="{C_PINK_L}" opacity="0.6"/>
""")

SVGS["dad"] = svg(f"""
  <rect x="36" y="12" width="28" height="10" rx="5" fill="{C_GRAY}"/>
  {face(50, 29, 13)}
  <rect x="37" y="44" width="26" height="26" rx="5" fill="{C_BLUE}"/>
  <line x1="37" y1="50" x2="22" y2="60" stroke="{C_BLUE}" stroke-width="7.5" stroke-linecap="round"/>
  <line x1="63" y1="50" x2="78" y2="60" stroke="{C_BLUE}" stroke-width="7.5" stroke-linecap="round"/>
  <line x1="44" y1="70" x2="43" y2="88" stroke="{C_GRAY}" stroke-width="6.5" stroke-linecap="round"/>
  <line x1="56" y1="70" x2="57" y2="88" stroke="{C_GRAY}" stroke-width="6.5" stroke-linecap="round"/>
""")

SVGS["your"] = svg(f"""
  {face(38, 28, 12)}
  <rect x="29" y="42" width="18" height="20" rx="4" fill="{C_AMBER}"/>
  <line x1="29" y1="47" x2="18" y2="57" stroke="{C_AMBER}" stroke-width="6" stroke-linecap="round"/>
  <line x1="47" y1="47" x2="58" y2="57" stroke="{C_AMBER}" stroke-width="6" stroke-linecap="round"/>
  <line x1="32" y1="62" x2="31" y2="76" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="44" y1="62" x2="45" y2="76" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <path d="M65 42 L78 42 M65 52 L78 52 M65 62 L78 62" stroke="{C_AMBER_D}" stroke-width="3" stroke-linecap="round"/>
  <path d="M58 35 L58 72" stroke="{C_AMBER_D}" stroke-width="2" stroke-dasharray="3,2"/>
""")

SVGS["them"] = svg(f"""
  {face(28, 32, 10)}
  <rect x="20" y="44" width="16" height="18" rx="3" fill="{C_AMBER}"/>
  <line x1="28" y1="62" x2="25" y2="74" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
  <line x1="32" y1="62" x2="34" y2="74" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
  {face(50, 32, 10)}
  <rect x="42" y="44" width="16" height="18" rx="3" fill="{C_ORANGE}"/>
  <line x1="50" y1="62" x2="47" y2="74" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
  <line x1="54" y1="62" x2="56" y2="74" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
  {face(72, 32, 10)}
  <rect x="64" y="44" width="16" height="18" rx="3" fill="{C_PINK}"/>
  <line x1="72" y1="62" x2="69" y2="74" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
  <line x1="76" y1="62" x2="78" y2="74" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
""")

SVGS["their"] = svg(f"""
  {face(28, 30, 10)}
  <rect x="20" y="42" width="16" height="16" rx="3" fill="{C_AMBER}"/>
  <line x1="28" y1="58" x2="26" y2="70" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
  <line x1="32" y1="58" x2="34" y2="70" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
  {face(72, 30, 10)}
  <rect x="64" y="42" width="16" height="16" rx="3" fill="{C_PINK}"/>
  <line x1="72" y1="58" x2="70" y2="70" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
  <line x1="76" y1="58" x2="78" y2="70" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
  <rect x="36" y="74" width="28" height="14" rx="4" fill="{C_AMBER_L}" stroke="{C_AMBER}" stroke-width="2"/>
  <text x="50" y="84" text-anchor="middle" font-size="7" font-weight="bold" fill="{C_AMBER_D}">THEIRS</text>
""")

SVGS["tummy"] = svg(f"""
  {face(50, 24, 13)}
  <rect x="38" y="39" width="24" height="22" rx="5" fill="{C_SKIN_D}"/>
  <ellipse cx="50" cy="52" rx="8" ry="6" fill="{C_SKIN}" stroke="{C_SKIN_D}" stroke-width="1.5"/>
  <circle cx="50" cy="52" r="2.5" fill="{C_ORANGE}" opacity="0.7"/>
  <line x1="44" y1="61" x2="42" y2="76" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="56" y1="61" x2="58" y2="76" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <path d="M40 43 Q30 52 40 61" stroke="{C_AMBER}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <path d="M60 43 Q70 52 60 61" stroke="{C_AMBER}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
""")

SVGS["that"] = svg(f"""
  <circle cx="50" cy="36" r="18" fill="{C_YELLOW_L}" stroke="{C_AMBER}" stroke-width="2.5"/>
  <circle cx="50" cy="36" r="8" fill="{C_AMBER}" opacity="0.5"/>
  <path d="M50 20 L50 10 M50 52 L50 62 M34 36 L24 36 M66 36 L76 36" stroke="{C_AMBER}" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M72 62 L85 72 M78 68 L85 72 L79 78" stroke="{C_AMBER_D}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
""")

SVGS["thats_funny"] = svg(f"""
  {face(50, 35, 18, mouth_type="grin", blush=True)}
  <path d="M20 65 Q18 80 30 82" stroke="{C_YELLOW}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <circle cx="33" cy="82" r="4" fill="{C_YELLOW}"/>
  <path d="M80 65 Q82 80 70 82" stroke="{C_YELLOW}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <circle cx="67" cy="82" r="4" fill="{C_YELLOW}"/>
  <text x="50" y="98" text-anchor="middle" font-size="9" fill="{C_AMBER_D}" font-weight="bold">HA HA!</text>
""")

SVGS["tummystomach"] = SVGS["tummy"]

# ════════════════════════════════════════════════════════════════
# CORE WORDS
# ════════════════════════════════════════════════════════════════

SVGS["want"] = svg(f"""
  <path d="M25 55 L50 25 L75 55" fill="none" stroke="{C_GREEN}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="50" cy="70" r="14" fill="{C_GREEN}" opacity="0.85"/>
  <path d="M43 70 L48 75 L57 64" stroke="white" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
""")

SVGS["need"] = svg(f"""
  <circle cx="50" cy="40" r="22" fill="none" stroke="{C_GREEN}" stroke-width="5"/>
  <rect x="46" y="24" width="8" height="22" rx="4" fill="{C_GREEN}"/>
  <rect x="46" y="50" width="8" height="8" rx="4" fill="{C_GREEN}"/>
  <path d="M18 72 Q50 85 82 72" stroke="{C_GREEN_D}" stroke-width="3.5" fill="none" stroke-linecap="round"/>
""")

SVGS["yes"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_GREEN}" opacity="0.15"/>
  <circle cx="50" cy="50" r="34" fill="{C_GREEN}"/>
  <path d="M28 50 L43 65 L72 35" stroke="white" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
""")

SVGS["no"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_RED}" opacity="0.15"/>
  <circle cx="50" cy="50" r="34" fill="{C_RED}"/>
  <line x1="30" y1="30" x2="70" y2="70" stroke="white" stroke-width="8" stroke-linecap="round"/>
  <line x1="70" y1="30" x2="30" y2="70" stroke="white" stroke-width="8" stroke-linecap="round"/>
""")

SVGS["more"] = svg(f"""
  <circle cx="50" cy="50" r="34" fill="{C_PURPLE}"/>
  <line x1="50" y1="30" x2="50" y2="70" stroke="white" stroke-width="8" stroke-linecap="round"/>
  <line x1="30" y1="50" x2="70" y2="50" stroke="white" stroke-width="8" stroke-linecap="round"/>
""")

SVGS["stop"] = svg(f"""
  <polygon points="50,8 79,21 88,52 72,81 28,81 12,52 21,21" fill="{C_RED}" stroke="#b91c1c" stroke-width="2.5"/>
  <rect x="38" y="28" width="24" height="8" rx="3" fill="white"/>
  <rect x="38" y="40" width="24" height="22" rx="3" fill="white"/>
""")

SVGS["help"] = svg(f"""
  <circle cx="50" cy="22" r="12" fill="{C_GREEN}"/>
  <circle cx="50" cy="22" r="8" fill="{C_GREEN_L}"/>
  <path d="M20 52 L38 38 L50 46 L62 38 L80 52" fill="none" stroke="{C_GREEN}" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="20" cy="52" r="6" fill="{C_GREEN}"/>
  <circle cx="80" cy="52" r="6" fill="{C_GREEN}"/>
  <path d="M25 70 L50 80 L75 70" stroke="{C_GREEN_D}" stroke-width="4" fill="none" stroke-linecap="round"/>
""")

SVGS["help_me"] = svg(f"""
  {face(50, 26, 13, mouth_type="open_smile")}
  <path d="M28 50 L20 42 M72 50 L80 42" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <rect x="34" y="42" width="32" height="24" rx="6" fill="{C_GREEN}"/>
  <path d="M34 52 L22 60 M66 52 L78 60" stroke="{C_GREEN}" stroke-width="7" stroke-linecap="round"/>
  <line x1="40" y1="66" x2="38" y2="82" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <line x1="60" y1="66" x2="62" y2="82" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
""")

SVGS["please"] = svg(f"""
  {face(50, 26, 13, blush=True)}
  <rect x="38" y="41" width="24" height="22" rx="5" fill="{C_PINK}"/>
  <path d="M38 47 L24 52 M62 47 L76 52" stroke="{C_PINK}" stroke-width="7" stroke-linecap="round"/>
  <path d="M30 54 Q20 62 28 70" stroke="{C_PINK_L}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <circle cx="28" cy="70" r="3.5" fill="{C_PINK_L}"/>
  <line x1="42" y1="63" x2="40" y2="78" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="58" y1="63" x2="60" y2="78" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
""")

SVGS["thank_you"] = svg(f"""
  {face(50, 26, 13, blush=True)}
  <rect x="38" y="41" width="24" height="22" rx="5" fill="{C_PINK}"/>
  <path d="M38 47 L24 55 M62 47 L76 55" stroke="{C_PINK}" stroke-width="7" stroke-linecap="round"/>
  <path d="M24 55 Q18 65 24 72" stroke="{C_PINK}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <circle cx="24" cy="72" r="4" fill="{C_PINK}"/>
  <line x1="42" y1="63" x2="40" y2="80" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="58" y1="63" x2="60" y2="80" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <path d="M60 78 Q72 84 78 76" stroke="{C_PINK}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <circle cx="78" cy="76" r="4" fill="{C_PINK}"/>
""")

SVGS["all_done"] = svg(f"""
  {face(50, 26, 13, mouth_type="smile")}
  <rect x="38" y="41" width="24" height="22" rx="5" fill="{C_GREEN}"/>
  <path d="M38 47 L22 40 M62 47 L78 40" stroke="{C_GREEN}" stroke-width="7" stroke-linecap="round"/>
  <path d="M22 40 L20 28 M78 40 L80 28" stroke="{C_GREEN}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="42" y1="63" x2="40" y2="78" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="58" y1="63" x2="60" y2="78" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <ellipse cx="50" cy="88" rx="22" ry="5" fill="{C_GREEN_L}" opacity="0.5"/>
  <path d="M36 88 L50 83 L64 88" stroke="{C_GREEN_D}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
""")

SVGS["good"] = svg(f"""
  {face(50, 32, 16, mouth_type="grin", blush=True)}
  <path d="M30 65 L25 78" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <path d="M25 78 L22 90 L34 90 L36 78" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="2" stroke-linejoin="round"/>
  <circle cx="22" cy="72" r="5" fill="{C_GREEN}"/>
  <path d="M70 65 L75 78 L75 90" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
""")

SVGS["bad"] = svg(f"""
  {face(50, 32, 16, mouth_type="frown")}
  <path d="M30 65 L25 78" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <path d="M25 78 L22 90 L34 90 L36 78" fill="{C_GRAY_L}" stroke="{C_GRAY}" stroke-width="2" stroke-linejoin="round"/>
  <path d="M22 90 L22 78 L25 78" fill="{C_RED}" stroke="none"/>
  <line x1="34" y1="24" x2="46" y2="26" stroke="{C_DARK}" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="54" y1="26" x2="66" y2="24" stroke="{C_DARK}" stroke-width="2.5" stroke-linecap="round"/>
""")

SVGS["hi"] = svg(f"""
  {face(50, 28, 14, blush=True, mouth_type="grin")}
  <rect x="38" y="44" width="24" height="22" rx="5" fill="{C_AMBER}"/>
  <path d="M62 46 L80 34" stroke="{C_AMBER}" stroke-width="7" stroke-linecap="round"/>
  <path d="M62 52 L82 48" stroke="{C_AMBER}" stroke-width="6" stroke-linecap="round"/>
  <path d="M62 58 L80 62" stroke="{C_AMBER}" stroke-width="6" stroke-linecap="round"/>
  <line x1="38" y1="46" x2="22" y2="54" stroke="{C_AMBER}" stroke-width="7" stroke-linecap="round"/>
  <line x1="42" y1="66" x2="40" y2="82" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="58" y1="66" x2="60" y2="82" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
""")

SVGS["hello"] = SVGS["hi"]
SVGS["hi_hello"] = SVGS["hi"]

SVGS["goodbye"] = svg(f"""
  {face(50, 28, 14, mouth_type="smile")}
  <rect x="38" y="44" width="24" height="22" rx="5" fill="{C_AMBER}"/>
  <path d="M62 46 L82 38 L84 26 L78 30 L80 18" stroke="{C_AMBER}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
  <line x1="38" y1="46" x2="22" y2="54" stroke="{C_AMBER}" stroke-width="7" stroke-linecap="round"/>
  <line x1="42" y1="66" x2="40" y2="82" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="58" y1="66" x2="60" y2="82" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
""")

SVGS["ok"] = svg(f"""
  <circle cx="50" cy="50" r="36" fill="{C_GREEN}" opacity="0.2"/>
  <circle cx="50" cy="50" r="30" fill="none" stroke="{C_GREEN}" stroke-width="5"/>
  <text x="50" y="58" text-anchor="middle" font-size="24" font-weight="bold" fill="{C_GREEN}" font-family="Arial, sans-serif">OK</text>
""")

SVGS["okfine"] = SVGS["ok"]
SVGS["fine"] = SVGS["ok"]

SVGS["space"] = svg(f"""
  {face(50, 32, 14, mouth_type="neutral")}
  <rect x="38" y="48" width="24" height="22" rx="5" fill="{C_BLUE}"/>
  <line x1="38" y1="54" x2="22" y2="62" stroke="{C_BLUE}" stroke-width="7" stroke-linecap="round"/>
  <line x1="62" y1="54" x2="78" y2="62" stroke="{C_BLUE}" stroke-width="7" stroke-linecap="round"/>
  <line x1="42" y1="70" x2="40" y2="84" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="58" y1="70" x2="60" y2="84" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <path d="M14 50 Q10 36 14 22 M86 50 Q90 36 86 22" stroke="{C_BLUE_L}" stroke-width="3" fill="none" stroke-linecap="round" stroke-dasharray="4,3"/>
""")

SVGS["too_loud"] = svg(f"""
  {face(50, 28, 14, mouth_type="open_smile")}
  <path d="M30 44 L20 38 M20 38 Q10 34 8 26" stroke="{C_ORANGE}" stroke-width="4.5" stroke-linecap="round" fill="none"/>
  <path d="M70 44 L80 38 M80 38 Q90 34 92 26" stroke="{C_ORANGE}" stroke-width="4.5" stroke-linecap="round" fill="none"/>
  <rect x="38" y="44" width="24" height="22" rx="5" fill="{C_ORANGE}"/>
  <line x1="38" y1="50" x2="23" y2="57" stroke="{C_ORANGE}" stroke-width="7" stroke-linecap="round"/>
  <line x1="62" y1="50" x2="77" y2="57" stroke="{C_ORANGE}" stroke-width="7" stroke-linecap="round"/>
  <path d="M23 52 Q12 44 14 34" stroke="{C_ORANGE}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M77 52 Q88 44 86 34" stroke="{C_ORANGE}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <line x1="42" y1="66" x2="40" y2="80" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="58" y1="66" x2="60" y2="80" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
""")

SVGS["i_need_a_break"] = svg(f"""
  {face(50, 22, 12, mouth_type="frown")}
  <rect x="38" y="36" width="24" height="20" rx="5" fill="{C_ORANGE}"/>
  <line x1="38" y1="42" x2="24" y2="50" stroke="{C_ORANGE}" stroke-width="6" stroke-linecap="round"/>
  <line x1="62" y1="42" x2="76" y2="50" stroke="{C_ORANGE}" stroke-width="6" stroke-linecap="round"/>
  <path d="M24 50 Q14 42 16 32" stroke="{C_ORANGE}" stroke-width="3.5" fill="none" stroke-linecap="round"/>
  <path d="M76 50 Q86 42 84 32" stroke="{C_ORANGE}" stroke-width="3.5" fill="none" stroke-linecap="round"/>
  <line x1="42" y1="56" x2="40" y2="70" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="58" y1="56" x2="60" y2="70" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <ellipse cx="50" cy="82" rx="26" ry="12" fill="{C_BLUE_L}" opacity="0.5"/>
  <text x="50" y="86" text-anchor="middle" font-size="8" font-weight="bold" fill="{C_BLUE_D}">BREAK</text>
""")

SVGS["i_want_water"] = svg(f"""
  {face(32, 24, 10)}
  <rect x="24" y="36" width="16" height="16" rx="4" fill="{C_AMBER}"/>
  <line x1="24" y1="40" x2="14" y2="47" stroke="{C_AMBER}" stroke-width="5" stroke-linecap="round"/>
  <line x1="40" y1="40" x2="52" y2="44" stroke="{C_AMBER}" stroke-width="5" stroke-linecap="round"/>
  <line x1="28" y1="52" x2="26" y2="64" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
  <line x1="36" y1="52" x2="38" y2="64" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
  <path d="M62 24 Q72 10 82 24 Q82 42 72 50 Q62 42 62 24Z" fill="{C_TEAL}" stroke="{C_TEAL_L}" stroke-width="1.5"/>
  <path d="M66 35 Q68 30 72 32" stroke="white" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.7"/>
""")

SVGS["i_need_the_bathroom"] = svg(f"""
  {face(28, 22, 10, mouth_type="frown")}
  <rect x="20" y="34" width="16" height="16" rx="4" fill="{C_GREEN}"/>
  <line x1="20" y1="38" x2="10" y2="46" stroke="{C_GREEN}" stroke-width="5" stroke-linecap="round"/>
  <line x1="36" y1="38" x2="46" y2="44" stroke="{C_GREEN}" stroke-width="5" stroke-linecap="round"/>
  <line x1="24" y1="50" x2="22" y2="62" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
  <line x1="32" y1="50" x2="34" y2="62" stroke="{C_GRAY}" stroke-width="4.5" stroke-linecap="round"/>
  <rect x="52" y="26" width="32" height="44" rx="6" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2.5"/>
  <ellipse cx="68" cy="58" rx="12" ry="8" fill="white" stroke="{C_BLUE}" stroke-width="2"/>
  <rect x="62" y="34" width="12" height="18" rx="4" fill="white" stroke="{C_BLUE}" stroke-width="1.5"/>
  <path d="M62 46 Q68 50 74 46" stroke="{C_BLUE}" stroke-width="1.5" fill="none"/>
""")

SVGS["i_dont_want_that"] = svg(f"""
  {face(30, 24, 12, mouth_type="frown")}
  <rect x="20" y="38" width="20" height="18" rx="4" fill="{C_RED}"/>
  <line x1="20" y1="43" x2="8" y2="50" stroke="{C_RED}" stroke-width="6" stroke-linecap="round"/>
  <line x1="40" y1="43" x2="52" y2="46" stroke="{C_RED}" stroke-width="6" stroke-linecap="round"/>
  <line x1="24" y1="56" x2="22" y2="70" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="36" y1="56" x2="38" y2="70" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <circle cx="72" cy="52" r="20" fill="{C_RED}" opacity="0.2"/>
  <circle cx="72" cy="52" r="16" fill="{C_RED}" opacity="0.85"/>
  <line x1="60" y1="40" x2="84" y2="64" stroke="white" stroke-width="5" stroke-linecap="round"/>
  <line x1="84" y1="40" x2="60" y2="64" stroke="white" stroke-width="5" stroke-linecap="round"/>
""")

SVGS["not"] = svg(f"""
  <circle cx="50" cy="50" r="34" fill="{C_GRAY_L}" stroke="{C_GRAY}" stroke-width="3"/>
  <line x1="32" y1="32" x2="68" y2="68" stroke="{C_RED}" stroke-width="7" stroke-linecap="round"/>
""")

SVGS["arent"] = SVGS["not"]
SVGS["cant"] = SVGS["not"]
SVGS["couldnt"] = SVGS["not"]
SVGS["havent"] = SVGS["not"]
SVGS["wont"] = SVGS["not"]

SVGS["know"] = svg(f"""
  {face(50, 32, 15)}
  <circle cx="50" cy="32" r="20" fill="none" stroke="{C_PURPLE}" stroke-width="3" stroke-dasharray="5,3" opacity="0.7"/>
  <path d="M32 70 Q50 90 68 70" stroke="{C_PURPLE}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <circle cx="50" cy="82" r="5" fill="{C_PURPLE}"/>
""")

# ════════════════════════════════════════════════════════════════
# ACTIONS / VERBS
# ════════════════════════════════════════════════════════════════

SVGS["eat"] = svg(f"""
  <ellipse cx="50" cy="70" rx="28" ry="16" fill="{C_ORANGE_L}" stroke="{C_ORANGE}" stroke-width="2.5"/>
  <circle cx="40" cy="66" r="7" fill="{C_RED}" opacity="0.85"/>
  <circle cx="56" cy="62" r="9" fill="{C_ORANGE}"/>
  <circle cx="52" cy="74" r="6" fill="{C_GREEN}"/>
  <path d="M50 46 L50 30" stroke="{C_GRAY}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M42 22 Q38 14 42 10" stroke="{C_GRAY}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M50 22 L50 14" stroke="{C_GRAY}" stroke-width="3" stroke-linecap="round"/>
  <path d="M58 22 Q62 14 58 10" stroke="{C_GRAY}" stroke-width="3" fill="none" stroke-linecap="round"/>
""")

SVGS["drink"] = svg(f"""
  <path d="M32 20 L36 82 Q36 88 44 88 L56 88 Q64 88 64 82 L68 20 Z" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2.5"/>
  <path d="M33 40 L67 40 L65 82 Q65 86 56 86 L44 86 Q35 86 35 82 Z" fill="{C_TEAL}" opacity="0.55"/>
  <ellipse cx="50" cy="20" rx="18" ry="3" fill="{C_BLUE}" opacity="0.7"/>
  <path d="M38 50 Q42 44 46 50 Q50 56 54 50" stroke="white" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.7"/>
""")

SVGS["go"] = svg(f"""
  <circle cx="38" cy="50" r="18" fill="{C_GREEN_L}"/>
  <path d="M38 50 L70 50" stroke="{C_GREEN}" stroke-width="7" stroke-linecap="round"/>
  <path d="M58 36 L76 50 L58 64" fill="{C_GREEN}" stroke="{C_GREEN_D}" stroke-width="1.5" stroke-linejoin="round"/>
  <circle cx="28" cy="62" r="5" fill="{C_GREEN}" opacity="0.5"/>
  <circle cx="22" cy="70" r="4" fill="{C_GREEN}" opacity="0.35"/>
  <circle cx="16" cy="78" r="3" fill="{C_GREEN}" opacity="0.2"/>
""")

SVGS["play"] = svg(f"""
  <circle cx="50" cy="50" r="34" fill="{C_PURPLE}" stroke="{C_PURPLE_L}" stroke-width="2"/>
  <polygon points="38,32 38,68 74,50" fill="white"/>
""")

SVGS["walk"] = svg(f"""
  <circle cx="50" cy="14" r="9" fill="{C_GREEN}"/>
  {face(50, 14, 9)}
  <line x1="50" y1="23" x2="50" y2="46" stroke="{C_GREEN}" stroke-width="7" stroke-linecap="round"/>
  <line x1="50" y1="32" x2="34" y2="44" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <line x1="50" y1="32" x2="66" y2="40" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <line x1="50" y1="46" x2="38" y2="66" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <line x1="50" y1="46" x2="62" y2="64" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <path d="M38 66 L34 80" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <path d="M62 64 L68 78" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
""")

SVGS["look"] = svg(f"""
  <ellipse cx="50" cy="50" rx="36" ry="22" fill="white" stroke="{C_GREEN}" stroke-width="4"/>
  <circle cx="50" cy="50" r="14" fill="{C_GREEN}"/>
  <circle cx="50" cy="50" r="7" fill="{C_DARK}"/>
  <circle cx="53" cy="47" r="3" fill="white"/>
""")

SVGS["give"] = svg(f"""
  <path d="M14 60 Q14 48 26 48 L44 48" stroke="{C_GREEN}" stroke-width="5.5" fill="none" stroke-linecap="round"/>
  <path d="M44 38 L44 58" stroke="{C_GREEN}" stroke-width="5.5" stroke-linecap="round"/>
  <path d="M36 46 L44 38 L52 46" stroke="{C_GREEN}" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="52" y="34" width="28" height="20" rx="5" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="2"/>
  <line x1="66" y1="34" x2="66" y2="54" stroke="{C_AMBER_D}" stroke-width="1.5"/>
  <line x1="52" y1="44" x2="80" y2="44" stroke="{C_AMBER_D}" stroke-width="1.5"/>
  <path d="M80 54 Q90 58 86 66" stroke="{C_AMBER}" stroke-width="3" fill="none" stroke-linecap="round"/>
""")

SVGS["feel"] = svg(f"""
  <circle cx="50" cy="42" r="22" fill="{C_YELLOW}" stroke="{C_AMBER}" stroke-width="2.5"/>
  <circle cx="40" cy="38" r="3" fill="{C_DARK}"/>
  <circle cx="60" cy="38" r="3" fill="{C_DARK}"/>
  <path d="M36 50 Q50 62 64 50" stroke="{C_DARK}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M24 72 Q28 84 38 84 L62 84 Q72 84 76 72" fill="{C_PINK_L}" stroke="{C_PINK}" stroke-width="2" opacity="0.8"/>
  <path d="M38 84 L50 90 L62 84" stroke="{C_PINK}" stroke-width="2" fill="none"/>
""")

SVGS["sleep"] = svg(f"""
  <circle cx="38" cy="40" r="18" fill="{C_PURPLE}"/>
  {face(38, 40, 18, skin=C_SKIN, mouth_type="neutral")}
  <ellipse cx="38" cy="53" rx="10" ry="3" fill="{C_PURPLE_L}" opacity="0.5"/>
  <text x="66" y="28" text-anchor="middle" font-size="16" font-weight="bold" fill="{C_PURPLE}">Z</text>
  <text x="78" y="18" text-anchor="middle" font-size="12" font-weight="bold" fill="{C_PURPLE_L}">z</text>
  <text x="86" y="11" text-anchor="middle" font-size="9" font-weight="bold" fill="{C_PURPLE_L}" opacity="0.6">z</text>
""")

SVGS["like"] = svg(f"""
  <path d="M50 80 C30 68 8 54 8 36 A18 18 0 0 1 50 28 A18 18 0 0 1 92 36 C92 54 70 68 50 80Z" fill="{C_PINK}" stroke="{C_ROSE}" stroke-width="2"/>
  <path d="M34 44 Q32 36 38 34" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.6"/>
""")

SVGS["break"] = svg(f"""
  {face(50, 26, 14, mouth_type="neutral")}
  <rect x="36" y="42" width="28" height="24" rx="6" fill="{C_BLUE}"/>
  <line x1="36" y1="48" x2="20" y2="56" stroke="{C_BLUE}" stroke-width="7" stroke-linecap="round"/>
  <line x1="64" y1="48" x2="80" y2="56" stroke="{C_BLUE}" stroke-width="7" stroke-linecap="round"/>
  <line x1="42" y1="66" x2="42" y2="80" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <line x1="58" y1="66" x2="58" y2="80" stroke="{C_GRAY}" stroke-width="6" stroke-linecap="round"/>
  <path d="M32 80 L68 80" stroke="{C_BLUE_L}" stroke-width="5" stroke-linecap="round"/>
  <path d="M20 86 L80 86" stroke="{C_BLUE_L}" stroke-width="3.5" stroke-linecap="round"/>
""")

SVGS["open"] = svg(f"""
  <rect x="18" y="28" width="64" height="50" rx="6" fill="{C_GREEN_L}" stroke="{C_GREEN}" stroke-width="3"/>
  <path d="M18 46 L82 46" stroke="{C_GREEN}" stroke-width="2.5" stroke-dasharray="4,3"/>
  <path d="M50 18 L50 28" stroke="{C_GREEN}" stroke-width="4" stroke-linecap="round"/>
  <path d="M38 20 L50 18 L62 20" stroke="{C_GREEN}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M26 46 L26 70 M50 46 L50 70 M74 46 L74 70" stroke="{C_GREEN}" stroke-width="2" stroke-dasharray="3,3" opacity="0.5"/>
""")

SVGS["close"] = svg(f"""
  <rect x="18" y="28" width="64" height="50" rx="6" fill="{C_GRAY_L}" stroke="{C_GRAY}" stroke-width="3"/>
  <path d="M18 28 L82 28" stroke="{C_GRAY}" stroke-width="4"/>
  <line x1="32" y1="42" x2="68" y2="42" stroke="{C_GRAY}" stroke-width="3" stroke-linecap="round"/>
  <line x1="32" y1="52" x2="68" y2="52" stroke="{C_GRAY}" stroke-width="3" stroke-linecap="round"/>
  <line x1="32" y1="62" x2="68" y2="62" stroke="{C_GRAY}" stroke-width="3" stroke-linecap="round"/>
  <path d="M36 16 L50 10 L64 16" stroke="{C_GRAY}" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M50 10 L50 28" stroke="{C_GRAY}" stroke-width="4" stroke-linecap="round"/>
""")

SVGS["turn"] = svg(f"""
  <path d="M20 50 Q20 20 50 20 Q80 20 80 50" fill="none" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <polygon points="76,36 88,50 76,64" fill="{C_GREEN}"/>
  <path d="M20 50 Q20 80 50 80 Q80 80 80 50" fill="none" stroke="{C_GREEN_L}" stroke-width="4" stroke-linecap="round" stroke-dasharray="5,3"/>
  <circle cx="50" cy="50" r="8" fill="{C_GREEN}" opacity="0.6"/>
""")

SVGS["run"] = svg(f"""
  <circle cx="60" cy="14" r="9" fill="{C_GREEN}"/>
  {face(60, 14, 9)}
  <line x1="60" y1="23" x2="50" y2="44" stroke="{C_GREEN}" stroke-width="6.5" stroke-linecap="round"/>
  <line x1="50" y1="32" x2="32" y2="28" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <line x1="50" y1="32" x2="68" y2="26" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <line x1="50" y1="44" x2="36" y2="62" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <line x1="50" y1="44" x2="66" y2="60" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <path d="M36 62 Q30 72 36 80" stroke="{C_GRAY}" stroke-width="5" fill="none" stroke-linecap="round"/>
  <path d="M66 60 L72 78" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <path d="M18 74 Q24 68 32 72 Q38 76 44 70" stroke="{C_GREEN_L}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
""")

SVGS["jump"] = svg(f"""
  <circle cx="50" cy="12" r="9" fill="{C_GREEN}"/>
  {face(50, 12, 9, mouth_type="grin")}
  <line x1="50" y1="21" x2="50" y2="46" stroke="{C_GREEN}" stroke-width="6.5" stroke-linecap="round"/>
  <line x1="50" y1="32" x2="30" y2="24" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <line x1="50" y1="32" x2="70" y2="24" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <line x1="50" y1="46" x2="36" y2="60" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <line x1="50" y1="46" x2="64" y2="60" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <path d="M30 80 L70 80" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <path d="M22 82 L78 82" stroke="{C_GRAY_L}" stroke-width="3" stroke-linecap="round" opacity="0.7"/>
  <path d="M36 62 Q34 72 38 78" stroke="{C_GRAY}" stroke-width="4.5" fill="none" stroke-linecap="round"/>
  <path d="M64 60 Q66 72 62 78" stroke="{C_GRAY}" stroke-width="4.5" fill="none" stroke-linecap="round"/>
""")

SVGS["read"] = svg(f"""
  <rect x="18" y="24" width="28" height="36" rx="3" fill="{C_BLUE}" stroke="{C_BLUE_D}" stroke-width="2"/>
  <rect x="21" y="24" width="25" height="36" rx="3" fill="{C_BLUE_L}"/>
  <rect x="24" y="28" width="18" height="3" rx="1.5" fill="white" opacity="0.7"/>
  <rect x="24" y="34" width="14" height="2.5" rx="1.2" fill="white" opacity="0.4"/>
  <rect x="24" y="40" width="16" height="2.5" rx="1.2" fill="white" opacity="0.4"/>
  <rect x="24" y="46" width="10" height="2.5" rx="1.2" fill="white" opacity="0.4"/>
  <line x1="20" y1="24" x2="20" y2="60" stroke="{C_BLUE_D}" stroke-width="2.5"/>
  <rect x="54" y="24" width="28" height="36" rx="3" fill="{C_BLUE}" stroke="{C_BLUE_D}" stroke-width="2"/>
  <rect x="54" y="24" width="25" height="36" rx="3" fill="{C_BLUE_L}"/>
  <rect x="57" y="28" width="18" height="3" rx="1.5" fill="white" opacity="0.7"/>
  <rect x="57" y="34" width="16" height="2.5" rx="1.2" fill="white" opacity="0.4"/>
  <rect x="57" y="40" width="14" height="2.5" rx="1.2" fill="white" opacity="0.4"/>
  <line x1="80" y1="24" x2="80" y2="60" stroke="{C_BLUE_D}" stroke-width="2.5"/>
  <path d="M46 28 Q50 24 54 28" stroke="{C_BLUE_D}" stroke-width="2" fill="none"/>
  {face(50, 78, 10, mouth_type="smile")}
""")

SVGS["hug"] = svg(f"""
  {face(50, 24, 12, blush=True, mouth_type="grin")}
  <rect x="40" y="38" width="20" height="20" rx="5" fill="{C_PINK}"/>
  <path d="M40 42 Q22 36 18 50 Q16 62 28 68" stroke="{C_PINK}" stroke-width="7" stroke-linecap="round" fill="none"/>
  <path d="M60 42 Q78 36 82 50 Q84 62 72 68" stroke="{C_PINK}" stroke-width="7" stroke-linecap="round" fill="none"/>
  <line x1="44" y1="58" x2="42" y2="74" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="56" y1="58" x2="58" y2="74" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <path d="M50 74 Q42 82 50 88 Q58 82 50 74Z" fill="{C_PINK_L}" opacity="0.6"/>
""")

SVGS["push"] = svg(f"""
  <circle cx="30" cy="22" r="9" fill="{C_GREEN}"/>
  {face(30, 22, 9)}
  <line x1="30" y1="31" x2="30" y2="52" stroke="{C_GREEN}" stroke-width="6.5" stroke-linecap="round"/>
  <line x1="30" y1="40" x2="18" y2="48" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <line x1="30" y1="40" x2="46" y2="50" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <line x1="30" y1="52" x2="22" y2="66" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="30" y1="52" x2="36" y2="68" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <path d="M46 50 L70 50" stroke="{C_GREEN}" stroke-width="5" stroke-linecap="round"/>
  <path d="M62 38 L78 50 L62 62" fill="{C_GREEN_L}" stroke="{C_GREEN}" stroke-width="2" stroke-linejoin="round"/>
""")

SVGS["make"] = svg(f"""
  <rect x="26" y="52" width="48" height="28" rx="5" fill="{C_ORANGE_L}" stroke="{C_ORANGE}" stroke-width="2.5"/>
  <rect x="22" y="46" width="56" height="12" rx="4" fill="{C_ORANGE}" stroke="{C_AMBER_D}" stroke-width="1.5"/>
  <rect x="32" y="26" width="14" height="20" rx="3" fill="{C_AMBER}"/>
  <rect x="54" y="32" width="14" height="14" rx="3" fill="{C_AMBER}"/>
  <circle cx="39" cy="20" r="8" fill="{C_AMBER_L}" stroke="{C_AMBER}" stroke-width="2"/>
  <circle cx="61" cy="24" r="6" fill="{C_AMBER_L}" stroke="{C_AMBER}" stroke-width="2"/>
""")

SVGS["work"] = svg(f"""
  <rect x="16" y="52" width="68" height="38" rx="6" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2.5"/>
  <rect x="26" y="58" width="48" height="24" rx="3" fill="{C_DARK}" opacity="0.85"/>
  <rect x="28" y="60" width="44" height="18" rx="2" fill="{C_BLUE_D}" opacity="0.7"/>
  <line x1="32" y1="64" x2="68" y2="64" stroke="{C_BLUE_L}" stroke-width="1.5" opacity="0.5"/>
  <line x1="32" y1="68" x2="60" y2="68" stroke="{C_BLUE_L}" stroke-width="1.5" opacity="0.5"/>
  <line x1="32" y1="72" x2="64" y2="72" stroke="{C_BLUE_L}" stroke-width="1.5" opacity="0.5"/>
  <rect x="36" y="40" width="28" height="12" rx="5" fill="{C_GRAY}"/>
  <rect x="40" y="44" width="20" height="4" rx="2" fill="{C_GRAY_L}"/>
  {face(50, 24, 12)}
""")

SVGS["see"] = svg(f"""
  <ellipse cx="50" cy="50" rx="36" ry="22" fill="{C_YELLOW_L}" stroke="{C_AMBER}" stroke-width="3"/>
  <circle cx="50" cy="50" r="12" fill="{C_BLUE}"/>
  <circle cx="50" cy="50" r="6" fill="{C_DARK}"/>
  <circle cx="52" cy="48" r="2.5" fill="white"/>
  <path d="M14 50 Q6 30 14 10 M86 50 Q94 30 86 10" stroke="{C_AMBER_L}" stroke-width="2" fill="none" stroke-linecap="round"/>
""")

SVGS["do"] = svg(f"""
  <circle cx="50" cy="28" r="14" fill="{C_GREEN}"/>
  {face(50, 28, 14)}
  <path d="M30 48 Q22 56 26 68 Q30 80 42 82" stroke="{C_GREEN}" stroke-width="5.5" fill="none" stroke-linecap="round"/>
  <path d="M70 48 Q78 56 74 68 Q70 80 58 82" stroke="{C_GREEN}" stroke-width="5.5" fill="none" stroke-linecap="round"/>
  <path d="M36 44 L64 44" stroke="{C_GREEN}" stroke-width="5.5" stroke-linecap="round"/>
""")

SVGS["slide"] = svg(f"""
  <circle cx="24" cy="22" r="8" fill="{C_PURPLE}"/>
  {face(24, 22, 8)}
  <path d="M24 30 L24 44" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <path d="M24 44 L72 78" stroke="{C_PURPLE}" stroke-width="8" stroke-linecap="round"/>
  <rect x="14" y="12" width="20" height="6" rx="3" fill="{C_GRAY}"/>
  <rect x="14" y="18" width="4" height="32" rx="2" fill="{C_GRAY}"/>
  <circle cx="72" cy="80" r="5" fill="{C_GRAY}"/>
  <circle cx="82" cy="85" r="4" fill="{C_GRAY}" opacity="0.5"/>
""")

SVGS["swing"] = svg(f"""
  <line x1="20" y1="10" x2="38" y2="56" stroke="{C_GRAY}" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="80" y1="10" x2="62" y2="56" stroke="{C_GRAY}" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="18" y1="10" x2="82" y2="10" stroke="{C_GRAY}" stroke-width="4" stroke-linecap="round"/>
  <rect x="34" y="54" width="32" height="8" rx="4" fill="{C_AMBER}"/>
  <circle cx="50" cy="38" r="10" fill="{C_GREEN}"/>
  {face(50, 38, 10, mouth_type="grin")}
  <path d="M40 48 L40 54 M60 48 L60 54" stroke="{C_GRAY}" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="34" y1="62" x2="28" y2="82" stroke="{C_GRAY}" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="66" y1="62" x2="72" y2="82" stroke="{C_GRAY}" stroke-width="3.5" stroke-linecap="round"/>
""")

SVGS["spin"] = svg(f"""
  <circle cx="50" cy="50" r="32" fill="{C_PURPLE}" opacity="0.2"/>
  <path d="M50 18 Q82 18 82 50 Q82 82 50 82 Q18 82 18 50 Q18 26 38 18" fill="none" stroke="{C_PURPLE}" stroke-width="6" stroke-linecap="round"/>
  <polygon points="38,10 50,22 26,22" fill="{C_PURPLE}"/>
  <circle cx="50" cy="50" r="8" fill="{C_PURPLE}"/>
""")

SVGS["take"] = svg(f"""
  <path d="M60 34 Q76 34 76 50 Q76 66 60 66 L40 66 Q24 66 24 50" stroke="{C_GREEN}" stroke-width="5.5" fill="none" stroke-linecap="round"/>
  <path d="M22 38 Q22 22 36 22 L58 22" stroke="{C_GREEN}" stroke-width="5.5" fill="none" stroke-linecap="round"/>
  <path d="M52 14 L64 22 L52 30" fill="{C_GREEN}" stroke="{C_GREEN_D}" stroke-width="1" stroke-linejoin="round"/>
  <circle cx="50" cy="52" r="8" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="1.5"/>
""")

SVGS["tickle"] = svg(f"""
  {face(50, 28, 15, mouth_type="grin", blush=True)}
  <path d="M18 52 Q22 44 30 48 Q34 60 26 64" stroke="{C_PINK}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M82 52 Q78 44 70 48 Q66 60 74 64" stroke="{C_PINK}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <line x1="38" y1="44" x2="30" y2="52" stroke="{C_AMBER}" stroke-width="4" stroke-linecap="round"/>
  <line x1="62" y1="44" x2="70" y2="52" stroke="{C_AMBER}" stroke-width="4" stroke-linecap="round"/>
  <rect x="38" y="44" width="24" height="22" rx="5" fill="{C_AMBER}"/>
  <line x1="42" y1="66" x2="40" y2="82" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
  <line x1="58" y1="66" x2="60" y2="82" stroke="{C_GRAY}" stroke-width="5.5" stroke-linecap="round"/>
""")

SVGS["ticklesqueeze"] = SVGS["tickle"]
SVGS["squeeze"] = SVGS["tickle"]

SVGS["down"] = svg(f"""
  <path d="M50 16 L50 66" stroke="{C_BLUE}" stroke-width="7" stroke-linecap="round"/>
  <path d="M26 50 L50 76 L74 50" fill="{C_BLUE}" stroke="{C_BLUE_D}" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M24 82 L76 82" stroke="{C_BLUE_L}" stroke-width="5" stroke-linecap="round"/>
""")

SVGS["put"] = svg(f"""
  <path d="M50 16 L50 54" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <path d="M32 42 L50 58 L68 42" fill="{C_GREEN}" opacity="0.8"/>
  <circle cx="50" cy="12" r="10" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="2"/>
  <rect x="26" y="62" width="48" height="22" rx="5" fill="{C_GRAY_L}" stroke="{C_GRAY}" stroke-width="2.5"/>
""")

SVGS["look_at_me"] = svg(f"""
  {face(72, 24, 12, blush=True)}
  <ellipse cx="72" cy="24" rx="14" ry="14" fill="none" stroke="{C_AMBER}" stroke-width="2.5" stroke-dasharray="5,3"/>
  <path d="M20 36 Q18 50 28 56" fill="none" stroke="{C_GREEN}" stroke-width="4.5" stroke-linecap="round"/>
  <ellipse cx="26" cy="54" rx="16" ry="10" fill="{C_GREEN_L}" stroke="{C_GREEN}" stroke-width="2"/>
  <circle cx="26" cy="54" r="6" fill="{C_DARK}"/>
  <circle cx="28" cy="52" r="2" fill="white"/>
  <path d="M34 54 L58 38 L70 36" stroke="{C_AMBER}" stroke-width="3" stroke-dasharray="4,3" stroke-linecap="round" fill="none"/>
""")

SVGS["my_turn"] = svg(f"""
  {face(34, 26, 13, blush=True)}
  <rect x="23" y="41" width="22" height="20" rx="5" fill="{C_AMBER}"/>
  <line x1="23" y1="47" x2="10" y2="54" stroke="{C_AMBER}" stroke-width="6" stroke-linecap="round"/>
  <line x1="45" y1="47" x2="60" y2="50" stroke="{C_AMBER}" stroke-width="6" stroke-linecap="round"/>
  <line x1="28" y1="61" x2="27" y2="76" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="40" y1="61" x2="41" y2="76" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <path d="M60 50 Q80 30 80 55 Q80 70 68 70" stroke="{C_AMBER_D}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M72 62 L68 70 L76 72" stroke="{C_AMBER_D}" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
""")

SVGS["one_more_minute"] = svg(f"""
  <circle cx="50" cy="44" r="30" fill="{C_GRAY_L}" stroke="{C_GRAY}" stroke-width="3.5"/>
  <circle cx="50" cy="44" r="24" fill="white"/>
  <line x1="50" y1="44" x2="50" y2="22" stroke="{C_DARK}" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="50" y1="44" x2="66" y2="50" stroke="{C_RED}" stroke-width="3" stroke-linecap="round"/>
  <circle cx="50" cy="44" r="3.5" fill="{C_DARK}"/>
  <text x="50" y="90" text-anchor="middle" font-size="9" font-weight="bold" fill="{C_AMBER_D}" font-family="Arial, sans-serif">1 MINUTE</text>
""")

SVGS["want_help"] = svg(f"""
  <circle cx="32" cy="20" r="10" fill="{C_GREEN}"/>
  {face(32, 20, 10)}
  <rect x="22" y="32" width="20" height="18" rx="4" fill="{C_GREEN}"/>
  <path d="M22 36 L10 43" stroke="{C_GREEN}" stroke-width="6" stroke-linecap="round"/>
  <line x1="28" y1="50" x2="26" y2="62" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="36" y1="50" x2="38" y2="62" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <path d="M52 36 Q52 26 62 26 Q72 26 72 36 Q72 46 62 50" stroke="{C_AMBER}" stroke-width="4.5" fill="none" stroke-linecap="round"/>
  <circle cx="62" cy="54" r="4" fill="{C_AMBER}"/>
  <circle cx="62" cy="62" r="3.5" fill="{C_AMBER}"/>
""")

SVGS["want_help_want_item"] = SVGS["want_help"]
SVGS["want_item"] = SVGS["want_help"]
SVGS["i_need_help"] = SVGS["help_me"]
SVGS["i_need_help_stop"] = SVGS["stop"]
SVGS["i_like_this"] = SVGS["like"]
SVGS["i_want_food"] = SVGS["eat"]
SVGS["i_want_apple"] = SVGS["eat"]
SVGS["i_want_a_jacket"] = svg(f"""
  <path d="M22 32 L10 44 L14 48 L26 40" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M78 32 L90 44 L86 48 L74 40" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M28 22 L22 32 L26 40 L36 36 L36 78 L64 78 L64 36 L74 40 L78 32 L72 22 L62 26 Q50 30 38 26 Z" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M50 26 L50 78" stroke="{C_BLUE}" stroke-width="2.5" stroke-dasharray="3,3"/>
  <circle cx="50" cy="40" r="3" fill="{C_BLUE}"/>
  <circle cx="50" cy="52" r="3" fill="{C_BLUE}"/>
  <circle cx="50" cy="64" r="3" fill="{C_BLUE}"/>
""")
SVGS["help_me_im_frustrated"] = SVGS["help_me"]
SVGS["no_i_dont_want_that"] = SVGS["i_dont_want_that"]
SVGS["too_loud_i_need_a_break"] = SVGS["too_loud"]
SVGS["play_doh"] = svg(f"""
  <rect x="26" y="44" width="48" height="38" rx="8" fill="{C_ORANGE}" stroke="{C_AMBER_D}" stroke-width="2.5"/>
  <rect x="36" y="36" width="28" height="14" rx="5" fill="{C_ORANGE_L}" stroke="{C_AMBER}" stroke-width="2"/>
  <path d="M26 52 L74 52" stroke="{C_AMBER_D}" stroke-width="1.5"/>
  <path d="M46 20 Q50 8 54 20 Q58 32 50 36 Q42 32 46 20Z" fill="{C_GREEN}" stroke="{C_GREEN_D}" stroke-width="1.5"/>
  <text x="50" y="68" text-anchor="middle" font-size="9" font-weight="bold" fill="white" font-family="Arial, sans-serif">PLAY</text>
  <text x="50" y="79" text-anchor="middle" font-size="9" font-weight="bold" fill="white" font-family="Arial, sans-serif">DOH</text>
""")

SVGS["doll"] = svg(f"""
  {face(50, 24, 13, blush=True, mouth_type="grin")}
  <ellipse cx="50" cy="20" rx="15" ry="6" fill="{C_AMBER}"/>
  <rect x="38" y="39" width="24" height="22" rx="5" fill="{C_PINK}"/>
  <path d="M38 43 L24 52 M62 43 L76 52" stroke="{C_PINK}" stroke-width="6" stroke-linecap="round"/>
  <path d="M38 61 Q50 74 62 61 L62 61 Q62 84 50 88 Q38 84 38 61Z" fill="{C_PINK_L}"/>
  <circle cx="50" cy="90" r="3" fill="{C_PINK}" opacity="0.5"/>
""")

SVGS["dog"] = svg(f"""
  <ellipse cx="50" cy="44" rx="26" ry="22" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="2"/>
  <ellipse cx="34" cy="28" rx="10" ry="14" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="2"/>
  <ellipse cx="66" cy="26" rx="8" ry="12" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="2"/>
  <circle cx="42" cy="44" r="5" fill="{C_DARK}"/>
  <circle cx="58" cy="44" r="5" fill="{C_DARK}"/>
  <circle cx="43" cy="43" r="2" fill="white"/>
  <circle cx="59" cy="43" r="2" fill="white"/>
  <ellipse cx="50" cy="54" rx="10" ry="6" fill="{C_SKIN_D}" stroke="{C_AMBER_D}" stroke-width="1.5"/>
  <path d="M44 54 Q50 60 56 54" stroke="{C_DARK}" stroke-width="1.5" fill="none"/>
  <path d="M66 56 Q78 48 82 62 Q84 70 72 72" stroke="{C_AMBER}" stroke-width="5" fill="none" stroke-linecap="round"/>
  <line x1="30" y1="70" x2="26" y2="90" stroke="{C_AMBER}" stroke-width="4" stroke-linecap="round"/>
  <line x1="42" y1="70" x2="40" y2="90" stroke="{C_AMBER}" stroke-width="4" stroke-linecap="round"/>
  <line x1="56" y1="70" x2="58" y2="90" stroke="{C_AMBER}" stroke-width="4" stroke-linecap="round"/>
  <line x1="68" y1="70" x2="72" y2="90" stroke="{C_AMBER}" stroke-width="4" stroke-linecap="round"/>
""")

# ════════════════════════════════════════════════════════════════
# FEELINGS
# ════════════════════════════════════════════════════════════════

SVGS["happy"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_YELLOW}" stroke="{C_AMBER}" stroke-width="2.5"/>
  <circle cx="37" cy="42" r="5" fill="{C_DARK}"/>
  <circle cx="63" cy="42" r="5" fill="{C_DARK}"/>
  <circle cx="38.5" cy="40.5" r="2" fill="white"/>
  <circle cx="64.5" cy="40.5" r="2" fill="white"/>
  <path d="M28 58 Q50 76 72 58" stroke="{C_DARK}" stroke-width="5" fill="none" stroke-linecap="round"/>
  <circle cx="30" cy="52" r="5" fill="{C_ROSE}" opacity="0.4"/>
  <circle cx="70" cy="52" r="5" fill="{C_ROSE}" opacity="0.4"/>
""")

SVGS["sad"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2.5"/>
  <circle cx="37" cy="42" r="5" fill="{C_DARK}"/>
  <circle cx="63" cy="42" r="5" fill="{C_DARK}"/>
  <circle cx="38.5" cy="40.5" r="2" fill="white"/>
  <circle cx="64.5" cy="40.5" r="2" fill="white"/>
  <path d="M28 66 Q50 52 72 66" stroke="{C_DARK}" stroke-width="5" fill="none" stroke-linecap="round"/>
  <line x1="36" y1="34" x2="44" y2="36" stroke="{C_DARK}" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="56" y1="36" x2="64" y2="34" stroke="{C_DARK}" stroke-width="2.5" stroke-linecap="round"/>
  <path d="M32 52 L30 62" stroke="{C_BLUE}" stroke-width="2" stroke-linecap="round"/>
  <path d="M68 52 L70 62" stroke="{C_BLUE}" stroke-width="2" stroke-linecap="round"/>
""")

SVGS["mad"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_RED}" opacity="0.85" stroke="#b91c1c" stroke-width="2.5"/>
  <circle cx="37" cy="44" r="5" fill="{C_DARK}"/>
  <circle cx="63" cy="44" r="5" fill="{C_DARK}"/>
  <circle cx="38.5" cy="42.5" r="2" fill="white"/>
  <circle cx="64.5" cy="42.5" r="2" fill="white"/>
  <path d="M28 62 Q50 50 72 62" stroke="{C_DARK}" stroke-width="5" fill="none" stroke-linecap="round"/>
  <line x1="28" y1="32" x2="46" y2="38" stroke="{C_DARK}" stroke-width="4" stroke-linecap="round"/>
  <line x1="72" y1="32" x2="54" y2="38" stroke="{C_DARK}" stroke-width="4" stroke-linecap="round"/>
""")

SVGS["made"] = SVGS["mad"]

SVGS["tired"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_PURPLE_L}" stroke="{C_PURPLE}" stroke-width="2.5"/>
  <path d="M32 42 Q50 52 68 42" stroke="{C_DARK}" stroke-width="4" fill="{C_PURPLE_L}"/>
  <path d="M32 42 Q50 48 68 42" fill="{C_SKIN_D}" opacity="0.8"/>
  <circle cx="37" cy="44" r="4" fill="{C_DARK}" opacity="0.7"/>
  <circle cx="63" cy="44" r="4" fill="{C_DARK}" opacity="0.7"/>
  <path d="M32 62 Q50 56 68 62" stroke="{C_DARK}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <text x="76" y="26" text-anchor="middle" font-size="14" font-weight="bold" fill="{C_PURPLE}">Z</text>
  <text x="86" y="18" text-anchor="middle" font-size="10" font-weight="bold" fill="{C_PURPLE_L}">z</text>
""")

SVGS["frustrated"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_ORANGE}" opacity="0.9" stroke="{C_AMBER_D}" stroke-width="2.5"/>
  <circle cx="37" cy="44" r="5" fill="{C_DARK}"/>
  <circle cx="63" cy="44" r="5" fill="{C_DARK}"/>
  <path d="M28 62 Q50 52 72 62" stroke="{C_DARK}" stroke-width="5" fill="none" stroke-linecap="round"/>
  <line x1="30" y1="32" x2="46" y2="37" stroke="{C_DARK}" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="70" y1="32" x2="54" y2="37" stroke="{C_DARK}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M28 44 Q20 38 22 30" stroke="{C_AMBER_D}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M72 44 Q80 38 78 30" stroke="{C_AMBER_D}" stroke-width="3" fill="none" stroke-linecap="round"/>
""")

SVGS["nervous"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_YELLOW_L}" stroke="{C_YELLOW}" stroke-width="2.5"/>
  <circle cx="37" cy="44" r="5" fill="{C_DARK}"/>
  <circle cx="63" cy="44" r="5" fill="{C_DARK}"/>
  <circle cx="38.5" cy="42.5" r="2" fill="white"/>
  <circle cx="64.5" cy="42.5" r="2" fill="white"/>
  <path d="M34 62 Q38 58 42 62 Q46 66 50 62 Q54 58 58 62 Q62 66 66 62" stroke="{C_DARK}" stroke-width="3.5" fill="none" stroke-linecap="round"/>
  <path d="M28 54 Q22 48 24 40" stroke="{C_YELLOW}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M72 54 Q78 48 76 40" stroke="{C_YELLOW}" stroke-width="3" fill="none" stroke-linecap="round"/>
""")

SVGS["sick"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="#86efac" stroke="{C_GREEN_D}" stroke-width="2.5"/>
  <circle cx="37" cy="44" r="5" fill="{C_DARK}"/>
  <circle cx="63" cy="44" r="5" fill="{C_DARK}"/>
  <path d="M34 60 Q50 54 66 60" stroke="{C_DARK}" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M34 56 Q50 68 66 56" fill="#86efac" stroke="{C_DARK}" stroke-width="2" opacity="0.5"/>
  <circle cx="30" cy="36" r="6" fill="white" stroke="#86efac" stroke-width="1.5"/>
  <circle cx="30" cy="36" r="3" fill="#86efac"/>
  <circle cx="70" cy="32" r="5" fill="white" stroke="#86efac" stroke-width="1.5"/>
  <circle cx="70" cy="32" r="2.5" fill="#86efac"/>
""")

SVGS["i_am_tired"] = SVGS["tired"]
SVGS["im_frustrated"] = SVGS["frustrated"]

# ════════════════════════════════════════════════════════════════
# PLACES / THINGS
# ════════════════════════════════════════════════════════════════

SVGS["bathroom"] = svg(f"""
  <rect x="18" y="20" width="64" height="60" rx="6" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2.5"/>
  <rect x="26" y="30" width="20" height="14" rx="3" fill="white" stroke="{C_BLUE}" stroke-width="1.5"/>
  <ellipse cx="56" cy="52" rx="16" ry="12" fill="white" stroke="{C_BLUE}" stroke-width="2"/>
  <ellipse cx="56" cy="54" rx="12" ry="8" fill="{C_BLUE_L}" opacity="0.4"/>
  <rect x="50" y="26" width="12" height="20" rx="3" fill="white" stroke="{C_BLUE}" stroke-width="1.5"/>
  <rect x="53" y="24" width="6" height="6" rx="1" fill="{C_GRAY_L}"/>
  <rect x="22" y="72" width="56" height="6" rx="2" fill="{C_BLUE}" opacity="0.3"/>
""")

SVGS["water"] = svg(f"""
  <path d="M50 12 Q70 36 70 54 A20 20 0 0 1 30 54 Q30 36 50 12Z" fill="{C_TEAL}" stroke="{C_TEAL_L}" stroke-width="2"/>
  <path d="M38 46 Q40 38 44 42" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.7"/>
  <ellipse cx="50" cy="68" rx="24" ry="8" fill="{C_TEAL}" opacity="0.3"/>
""")

SVGS["home"] = svg(f"""
  <path d="M50 10 L12 42 L18 42 L18 82 L82 82 L82 42 L88 42 Z" fill="{C_BLUE}" stroke="{C_BLUE_D}" stroke-width="2.5"/>
  <rect x="42" y="50" width="16" height="32" rx="2" fill="{C_AMBER}"/>
  <circle cx="54" cy="66" r="2.5" fill="{C_AMBER_D}"/>
  <rect x="24" y="52" width="14" height="12" rx="2" fill="{C_BLUE_L}" opacity="0.8"/>
  <rect x="62" y="52" width="14" height="12" rx="2" fill="{C_BLUE_L}" opacity="0.8"/>
  <path d="M24 55 L31 55 M24 60 L31 60 M31 52 L31 64" stroke="{C_BLUE}" stroke-width="1.5" opacity="0.5"/>
  <path d="M62 55 L69 55 M62 60 L69 60 M69 52 L69 64" stroke="{C_BLUE}" stroke-width="1.5" opacity="0.5"/>
""")

SVGS["school"] = svg(f"""
  <rect x="14" y="38" width="72" height="44" rx="4" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="2.5"/>
  <path d="M50 14 L14 38 L86 38 Z" fill="{C_YELLOW}" stroke="{C_AMBER_D}" stroke-width="2.5"/>
  <rect x="28" y="50" width="12" height="10" rx="2" fill="{C_BLUE_L}"/>
  <rect x="60" y="50" width="12" height="10" rx="2" fill="{C_BLUE_L}"/>
  <rect x="44" y="56" width="12" height="26" rx="2" fill="{C_AMBER_D}"/>
  <rect x="48" y="24" width="4" height="12" rx="2" fill="{C_AMBER_D}"/>
  <circle cx="50" cy="22" r="5" fill="{C_RED}"/>
""")

SVGS["food"] = svg(f"""
  <ellipse cx="50" cy="62" rx="34" ry="16" fill="{C_GRAY_L}" stroke="{C_GRAY}" stroke-width="2"/>
  <ellipse cx="50" cy="60" rx="34" ry="16" fill="{C_GRAY_L}"/>
  <ellipse cx="50" cy="58" rx="30" ry="12" fill="white" stroke="{C_GRAY_L}" stroke-width="1.5"/>
  <circle cx="38" cy="52" r="8" fill="{C_RED}" opacity="0.9"/>
  <circle cx="55" cy="48" r="10" fill="{C_ORANGE}"/>
  <circle cx="64" cy="54" r="7" fill="{C_GREEN}"/>
  <path d="M52 24 Q52 14 60 10" stroke="{C_GRAY}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <circle cx="48" cy="26" r="4" fill="none" stroke="{C_GRAY}" stroke-width="2.5"/>
  <circle cx="62" cy="22" r="3.5" fill="none" stroke="{C_GRAY}" stroke-width="2.5"/>
""")

SVGS["toy"] = svg(f"""
  <circle cx="50" cy="32" r="16" fill="{C_PURPLE}" stroke="{C_PURPLE_L}" stroke-width="2.5"/>
  {face(50, 32, 16)}
  <circle cx="50" cy="20" r="4" fill="{C_PINK}"/>
  <rect x="46" y="48" width="8" height="14" rx="4" fill="{C_PURPLE_L}"/>
  <circle cx="36" cy="56" r="6" fill="{C_PURPLE}"/>
  <circle cx="64" cy="56" r="6" fill="{C_PURPLE}"/>
""")

SVGS["book"] = svg(f"""
  <rect x="16" y="18" width="32" height="64" rx="3" fill="{C_BLUE}" stroke="{C_BLUE_D}" stroke-width="2"/>
  <rect x="18" y="18" width="30" height="64" rx="3" fill="{C_BLUE_L}"/>
  <rect x="21" y="24" width="22" height="4" rx="2" fill="white" opacity="0.7"/>
  <rect x="21" y="32" width="18" height="3" rx="1.5" fill="white" opacity="0.4"/>
  <rect x="21" y="38" width="20" height="3" rx="1.5" fill="white" opacity="0.4"/>
  <rect x="21" y="44" width="15" height="3" rx="1.5" fill="white" opacity="0.4"/>
  <line x1="18" y1="18" x2="18" y2="82" stroke="{C_BLUE_D}" stroke-width="3"/>
  <rect x="52" y="18" width="32" height="64" rx="3" fill="{C_BLUE}" stroke="{C_BLUE_D}" stroke-width="2"/>
  <rect x="52" y="18" width="30" height="64" rx="3" fill="{C_BLUE_L}"/>
  <rect x="55" y="24" width="22" height="4" rx="2" fill="white" opacity="0.7"/>
  <rect x="55" y="32" width="20" height="3" rx="1.5" fill="white" opacity="0.4"/>
  <rect x="55" y="38" width="18" height="3" rx="1.5" fill="white" opacity="0.4"/>
  <line x1="82" y1="18" x2="82" y2="82" stroke="{C_BLUE_D}" stroke-width="3"/>
  <path d="M48 22 Q50 18 52 22" stroke="{C_BLUE_D}" stroke-width="2" fill="none"/>
""")

SVGS["books"] = SVGS["book"]

SVGS["car"] = svg(f"""
  <rect x="12" y="44" width="76" height="30" rx="8" fill="{C_BLUE}" stroke="{C_BLUE_D}" stroke-width="2.5"/>
  <path d="M26 44 L36 22 L64 22 L74 44" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2"/>
  <rect x="38" y="26" width="24" height="16" rx="3" fill="{C_TEAL_L}" opacity="0.8"/>
  <circle cx="28" cy="78" r="12" fill="{C_DARK}" stroke="{C_GRAY}" stroke-width="2"/>
  <circle cx="28" cy="78" r="6" fill="{C_GRAY}"/>
  <circle cx="72" cy="78" r="12" fill="{C_DARK}" stroke="{C_GRAY}" stroke-width="2"/>
  <circle cx="72" cy="78" r="6" fill="{C_GRAY}"/>
  <circle cx="80" cy="56" r="4" fill="{C_YELLOW}" opacity="0.9"/>
""")

SVGS["bus"] = svg(f"""
  <rect x="10" y="30" width="80" height="48" rx="8" fill="{C_YELLOW}" stroke="{C_AMBER_D}" stroke-width="2.5"/>
  <rect x="14" y="34" width="22" height="20" rx="3" fill="{C_TEAL_L}" opacity="0.8" stroke="{C_AMBER}" stroke-width="1.5"/>
  <rect x="40" y="34" width="22" height="20" rx="3" fill="{C_TEAL_L}" opacity="0.8" stroke="{C_AMBER}" stroke-width="1.5"/>
  <rect x="66" y="34" width="18" height="20" rx="3" fill="{C_TEAL_L}" opacity="0.8" stroke="{C_AMBER}" stroke-width="1.5"/>
  <circle cx="26" cy="80" r="11" fill="{C_DARK}" stroke="{C_GRAY}" stroke-width="2"/>
  <circle cx="26" cy="80" r="5" fill="{C_GRAY}"/>
  <circle cx="74" cy="80" r="11" fill="{C_DARK}" stroke="{C_GRAY}" stroke-width="2"/>
  <circle cx="74" cy="80" r="5" fill="{C_GRAY}"/>
  <rect x="10" y="58" width="80" height="10" fill="{C_AMBER_D}" opacity="0.3"/>
  <rect x="80" y="38" width="10" height="8" rx="2" fill="{C_RED}" opacity="0.8"/>
""")

SVGS["airplane"] = svg(f"""
  <path d="M12 54 L48 34 L88 50 L48 44 Z" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2"/>
  <path d="M48 44 L48 72 L60 68 L60 50" fill="{C_BLUE}" stroke="{C_BLUE_D}" stroke-width="1.5"/>
  <path d="M20 54 L36 66 L48 62" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="1.5"/>
  <path d="M48 44 L88 50 L48 34 Z" fill="{C_BLUE}" opacity="0.6"/>
  <circle cx="74" cy="46" r="5" fill="{C_TEAL_L}" opacity="0.7"/>
  <circle cx="60" cy="42" r="5" fill="{C_TEAL_L}" opacity="0.7"/>
""")

SVGS["train"] = svg(f"""
  <rect x="18" y="24" width="64" height="50" rx="10" fill="{C_RED}" stroke="#b91c1c" stroke-width="2.5"/>
  <rect x="26" y="34" width="20" height="18" rx="4" fill="{C_TEAL_L}" opacity="0.85"/>
  <rect x="54" y="34" width="20" height="18" rx="4" fill="{C_TEAL_L}" opacity="0.85"/>
  <circle cx="32" cy="76" r="10" fill="{C_DARK}" stroke="{C_GRAY}" stroke-width="2"/>
  <circle cx="32" cy="76" r="5" fill="{C_GRAY}"/>
  <circle cx="68" cy="76" r="10" fill="{C_DARK}" stroke="{C_GRAY}" stroke-width="2"/>
  <circle cx="68" cy="76" r="5" fill="{C_GRAY}"/>
  <path d="M10 74 L90 74" stroke="{C_GRAY}" stroke-width="4" stroke-linecap="round"/>
  <rect x="44" y="14" width="12" height="14" rx="3" fill="{C_GRAY}"/>
  <path d="M40 14 L60 14" stroke="{C_GRAY}" stroke-width="3" stroke-linecap="round"/>
""")

SVGS["playground"] = svg(f"""
  <line x1="22" y1="16" x2="22" y2="82" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="78" y1="16" x2="78" y2="82" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="22" y1="16" x2="78" y2="16" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="32" y1="16" x2="44" y2="56" stroke="{C_GRAY}" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="68" y1="16" x2="56" y2="56" stroke="{C_GRAY}" stroke-width="3.5" stroke-linecap="round"/>
  <rect x="38" y="54" width="24" height="8" rx="4" fill="{C_AMBER}"/>
  <circle cx="38" cy="38" r="10" fill="{C_GREEN}"/>
  {face(38, 38, 10, mouth_type="grin")}
  <path d="M8 84 L92 84" stroke="{C_GREEN_L}" stroke-width="5" stroke-linecap="round" opacity="0.7"/>
""")

SVGS["trampoline"] = svg(f"""
  <circle cx="50" cy="28" r="12" fill="{C_GREEN}"/>
  {face(50, 28, 12, mouth_type="grin")}
  <ellipse cx="50" cy="66" rx="36" ry="12" fill="{C_PURPLE_L}" stroke="{C_PURPLE}" stroke-width="3"/>
  <ellipse cx="50" cy="66" rx="30" ry="8" fill="{C_BLUE_L}" opacity="0.6"/>
  <line x1="14" y1="70" x2="14" y2="90" stroke="{C_GRAY}" stroke-width="4" stroke-linecap="round"/>
  <line x1="86" y1="70" x2="86" y2="90" stroke="{C_GRAY}" stroke-width="4" stroke-linecap="round"/>
  <line x1="14" y1="66" x2="32" y2="58" stroke="{C_GRAY}" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="86" y1="66" x2="68" y2="58" stroke="{C_GRAY}" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="42" y1="40" x2="44" y2="54" stroke="{C_GRAY}" stroke-width="3" stroke-linecap="round"/>
  <line x1="58" y1="40" x2="56" y2="54" stroke="{C_GRAY}" stroke-width="3" stroke-linecap="round"/>
""")

SVGS["in"] = svg(f"""
  <rect x="20" y="28" width="60" height="50" rx="6" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2.5"/>
  <rect x="38" y="48" width="24" height="30" rx="2" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="1.5"/>
  <circle cx="50" cy="63" r="2.5" fill="{C_AMBER_D}"/>
  <path d="M50 14 L50 28" stroke="{C_GREEN}" stroke-width="5" stroke-linecap="round"/>
  <path d="M36 20 L50 28 L64 20" fill="{C_GREEN}" stroke="{C_GREEN_D}" stroke-width="1" stroke-linejoin="round"/>
""")

SVGS["out"] = svg(f"""
  <rect x="20" y="28" width="60" height="50" rx="6" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2.5"/>
  <rect x="38" y="48" width="24" height="30" rx="2" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="1.5"/>
  <circle cx="50" cy="63" r="2.5" fill="{C_AMBER_D}"/>
  <path d="M50 14 L50 28" stroke="{C_ORANGE}" stroke-width="5" stroke-linecap="round"/>
  <path d="M36 22 L50 14 L64 22" fill="none" stroke="{C_ORANGE}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>
""")

SVGS["up"] = svg(f"""
  <path d="M50 16 L50 72" stroke="{C_BLUE}" stroke-width="7" stroke-linecap="round"/>
  <path d="M26 40 L50 14 L74 40" fill="{C_BLUE}" stroke="{C_BLUE_D}" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M24 82 L76 82" stroke="{C_BLUE_L}" stroke-width="5" stroke-linecap="round"/>
""")

SVGS["off"] = svg(f"""
  <circle cx="50" cy="50" r="34" fill="{C_GRAY_L}" stroke="{C_GRAY}" stroke-width="3"/>
  <path d="M50 18 L50 52" stroke="{C_DARK}" stroke-width="5.5" stroke-linecap="round"/>
  <path d="M32 28 Q14 36 14 52 Q14 80 50 80 Q86 80 86 52 Q86 36 68 28" stroke="{C_DARK}" stroke-width="5" fill="none" stroke-linecap="round"/>
""")

SVGS["mouth"] = svg(f"""
  <ellipse cx="50" cy="34" rx="30" ry="22" fill="{C_SKIN}" stroke="{C_SKIN_D}" stroke-width="2"/>
  <circle cx="38" cy="26" r="5" fill="{C_DARK}"/>
  <circle cx="62" cy="26" r="5" fill="{C_DARK}"/>
  <path d="M28 42 Q50 60 72 42" fill="{C_ROSE}" opacity="0.8" stroke="{C_SKIN_D}" stroke-width="1.5"/>
  <path d="M32 48 Q50 68 68 48" fill="{C_RED}" opacity="0.6"/>
  <rect x="36" y="56" width="28" height="10" rx="2" fill="white" opacity="0.9"/>
  <rect x="36" y="68" width="28" height="8" rx="2" fill="white" opacity="0.7"/>
""")

SVGS["pink"] = svg(f"""
  <rect x="14" y="14" width="72" height="72" rx="10" fill="{C_PINK_L}" stroke="{C_PINK}" stroke-width="3"/>
  <text x="50" y="60" text-anchor="middle" font-size="18" font-weight="bold" fill="{C_PINK}" font-family="Arial, sans-serif">Pink</text>
""")

SVGS["i_found_something"] = svg(f"""
  {face(32, 26, 12, mouth_type="grin")}
  <rect x="22" y="40" width="20" height="18" rx="4" fill="{C_AMBER}"/>
  <line x1="22" y1="45" x2="10" y2="52" stroke="{C_AMBER}" stroke-width="6" stroke-linecap="round"/>
  <line x1="42" y1="45" x2="56" y2="50" stroke="{C_AMBER}" stroke-width="6" stroke-linecap="round"/>
  <line x1="26" y1="58" x2="24" y2="72" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <line x1="38" y1="58" x2="40" y2="72" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <circle cx="74" cy="52" r="18" fill="{C_YELLOW_L}" stroke="{C_AMBER}" stroke-width="2.5"/>
  <path d="M67 44 Q74 36 82 42" stroke="{C_AMBER_D}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <circle cx="74" cy="52" r="6" fill="{C_AMBER}"/>
  <circle cx="74" cy="54" r="4" fill="{C_AMBER_D}"/>
""")

SVGS["classroom"] = svg(f"""
  <rect x="12" y="24" width="76" height="60" rx="5" fill="{C_YELLOW_L}" stroke="{C_AMBER}" stroke-width="2.5"/>
  <rect x="18" y="30" width="44" height="30" rx="3" fill="{C_GRAY_L}" stroke="{C_GRAY}" stroke-width="2"/>
  <line x1="20" y1="34" x2="60" y2="34" stroke="{C_GRAY}" stroke-width="1.5" opacity="0.5"/>
  <line x1="20" y1="40" x2="60" y2="40" stroke="{C_GRAY}" stroke-width="1.5" opacity="0.5"/>
  <line x1="20" y1="46" x2="60" y2="46" stroke="{C_GRAY}" stroke-width="1.5" opacity="0.5"/>
  <rect x="68" y="32" width="14" height="20" rx="2" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="1.5"/>
  <circle cx="75" cy="36" r="3" fill="{C_BLUE}"/>
  <rect x="18" y="66" width="64" height="12" rx="3" fill="{C_AMBER_L}" stroke="{C_AMBER}" stroke-width="1.5"/>
  <line x1="30" y1="66" x2="30" y2="78" stroke="{C_AMBER}" stroke-width="1.5"/>
  <line x1="46" y1="66" x2="46" y2="78" stroke="{C_AMBER}" stroke-width="1.5"/>
  <line x1="62" y1="66" x2="62" y2="78" stroke="{C_AMBER}" stroke-width="1.5"/>
""")

SVGS["gym"] = svg(f"""
  <rect x="12" y="36" width="76" height="52" rx="5" fill="{C_GRAY_L}" stroke="{C_GRAY}" stroke-width="2.5"/>
  <path d="M12 58 L88 58" stroke="{C_GRAY}" stroke-width="2" stroke-dasharray="4,3"/>
  <rect x="6" y="44" width="10" height="28" rx="3" fill="{C_GRAY}"/>
  <rect x="84" y="44" width="10" height="28" rx="3" fill="{C_GRAY}"/>
  <rect x="14" y="52" width="72" height="12" rx="4" fill="{C_GRAY}"/>
  <circle cx="32" cy="30" r="10" fill="{C_GREEN}"/>
  {face(32, 30, 10, mouth_type="grin")}
  <path d="M22 42 L18 50 M42 42 L46 52" stroke="{C_GREEN}" stroke-width="5" stroke-linecap="round"/>
""")

SVGS["game"] = svg(f"""
  <rect x="14" y="26" width="72" height="52" rx="10" fill="{C_PURPLE}" stroke="{C_PURPLE_L}" stroke-width="2.5"/>
  <circle cx="32" cy="52" r="6" fill="{C_GRAY_L}" opacity="0.7"/>
  <circle cx="68" cy="52" r="6" fill="{C_GRAY_L}" opacity="0.7"/>
  <rect x="44" y="44" width="12" height="12" rx="3" fill="{C_GRAY_L}" opacity="0.5"/>
  <circle cx="35" cy="38" r="5" fill="{C_RED}" opacity="0.8"/>
  <circle cx="65" cy="38" r="5" fill="{C_BLUE}" opacity="0.8"/>
  <line x1="26" y1="52" x2="38" y2="52" stroke="white" stroke-width="3" stroke-linecap="round"/>
  <line x1="32" y1="46" x2="32" y2="58" stroke="white" stroke-width="3" stroke-linecap="round"/>
""")

SVGS["ipad"] = svg(f"""
  <rect x="20" y="12" width="60" height="76" rx="8" fill="{C_DARK}" stroke="{C_GRAY}" stroke-width="2.5"/>
  <rect x="24" y="18" width="52" height="62" rx="4" fill="{C_BLUE_L}" opacity="0.9"/>
  <circle cx="50" cy="92" r="4" fill="{C_GRAY}"/>
  <circle cx="76" cy="18" r="2.5" fill="{C_GRAY}"/>
  <circle cx="50" cy="36" r="10" fill="{C_AMBER}" opacity="0.8"/>
  <circle cx="32" cy="56" r="7" fill="{C_GREEN}" opacity="0.7"/>
  <circle cx="50" cy="58" r="7" fill="{C_PURPLE}" opacity="0.7"/>
  <circle cx="68" cy="56" r="7" fill="{C_RED}" opacity="0.7"/>
""")

SVGS["music"] = svg(f"""
  <circle cx="30" cy="74" r="12" fill="{C_PURPLE_L}" stroke="{C_PURPLE}" stroke-width="2.5"/>
  <circle cx="30" cy="74" r="5" fill="{C_PURPLE}"/>
  <line x1="30" y1="62" x2="30" y2="22" stroke="{C_PURPLE}" stroke-width="4" stroke-linecap="round"/>
  <circle cx="66" cy="66" r="12" fill="{C_PURPLE_L}" stroke="{C_PURPLE}" stroke-width="2.5"/>
  <circle cx="66" cy="66" r="5" fill="{C_PURPLE}"/>
  <line x1="66" y1="54" x2="66" y2="14" stroke="{C_PURPLE}" stroke-width="4" stroke-linecap="round"/>
  <line x1="30" y1="22" x2="66" y2="14" stroke="{C_PURPLE}" stroke-width="4" stroke-linecap="round"/>
""")

SVGS["puzzle"] = svg(f"""
  <rect x="14" y="14" width="34" height="34" rx="4" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2"/>
  <circle cx="48" cy="22" r="6" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2"/>
  <circle cx="22" cy="48" r="6" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2"/>
  <rect x="52" y="14" width="34" height="34" rx="4" fill="{C_ORANGE}" stroke="{C_AMBER_D}" stroke-width="2"/>
  <circle cx="48" cy="31" r="6" fill="{C_ORANGE}" stroke="{C_AMBER_D}" stroke-width="2"/>
  <rect x="14" y="52" width="34" height="34" rx="4" fill="{C_GREEN_L}" stroke="{C_GREEN}" stroke-width="2"/>
  <circle cx="31" cy="48" r="6" fill="{C_GREEN_L}" stroke="{C_GREEN}" stroke-width="2"/>
  <rect x="52" y="52" width="34" height="34" rx="4" fill="{C_PINK_L}" stroke="{C_PINK}" stroke-width="2"/>
  <circle cx="31" cy="69" r="6" fill="{C_PINK_L}" stroke="{C_PINK}" stroke-width="2"/>
  <circle cx="69" cy="31" r="6" fill="{C_ORANGE}" stroke="{C_AMBER_D}" stroke-width="2"/>
""")

SVGS["bubbles"] = svg(f"""
  <circle cx="50" cy="60" r="22" fill="none" stroke="{C_TEAL}" stroke-width="3.5" opacity="0.9"/>
  <circle cx="50" cy="60" r="18" fill="{C_TEAL_L}" opacity="0.4"/>
  <path d="M40 50 Q38 44 44 44" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.7"/>
  <circle cx="26" cy="36" r="14" fill="none" stroke="{C_BLUE}" stroke-width="2.5" opacity="0.8"/>
  <path d="M20 30 Q18 26 22 26" stroke="white" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.6"/>
  <circle cx="72" cy="30" r="10" fill="none" stroke="{C_PURPLE}" stroke-width="2.5" opacity="0.8"/>
  <circle cx="80" cy="60" r="7" fill="none" stroke="{C_TEAL}" stroke-width="2" opacity="0.6"/>
  <circle cx="32" cy="72" r="6" fill="none" stroke="{C_BLUE}" stroke-width="2" opacity="0.5"/>
""")

# ════════════════════════════════════════════════════════════════
# BODY PARTS
# ════════════════════════════════════════════════════════════════

SVGS["ear"] = svg(f"""
  <ellipse cx="50" cy="50" rx="24" ry="38" fill="{C_SKIN}" stroke="{C_SKIN_D}" stroke-width="3"/>
  <ellipse cx="50" cy="50" rx="14" ry="26" fill="{C_SKIN_D}" opacity="0.5"/>
  <ellipse cx="50" cy="50" rx="6" ry="14" fill="{C_SKIN_D}" opacity="0.7"/>
""")

SVGS["eye"] = svg(f"""
  <ellipse cx="50" cy="50" rx="38" ry="28" fill="white" stroke="{C_DARK}" stroke-width="3"/>
  <circle cx="50" cy="50" r="15" fill="{C_BLUE}"/>
  <circle cx="50" cy="50" r="8" fill="{C_DARK}"/>
  <circle cx="54" cy="46" r="4" fill="white"/>
  <path d="M22 26 Q50 18 78 26" stroke="{C_AMBER_D}" stroke-width="4" fill="none" stroke-linecap="round"/>
""")

SVGS["hand"] = svg(f"""
  <path d="M36 78 L36 30 Q36 22 44 22 Q52 22 52 30 L52 50" stroke="{C_SKIN}" stroke-width="1" fill="{C_SKIN}" stroke-linejoin="round"/>
  <rect x="30" y="50" width="12" height="34" rx="6" fill="{C_SKIN}" stroke="{C_SKIN_D}" stroke-width="1.5"/>
  <rect x="44" y="24" width="12" height="36" rx="6" fill="{C_SKIN}" stroke="{C_SKIN_D}" stroke-width="1.5"/>
  <rect x="58" y="32" width="11" height="32" rx="5.5" fill="{C_SKIN}" stroke="{C_SKIN_D}" stroke-width="1.5"/>
  <rect x="69" y="36" width="10" height="28" rx="5" fill="{C_SKIN}" stroke="{C_SKIN_D}" stroke-width="1.5"/>
  <path d="M30 56 Q20 54 20 46 Q20 36 30 50" fill="{C_SKIN}" stroke="{C_SKIN_D}" stroke-width="1.5"/>
""")

SVGS["leg"] = svg(f"""
  <rect x="34" y="12" width="32" height="46" rx="8" fill="{C_SKIN}" stroke="{C_SKIN_D}" stroke-width="2.5"/>
  <rect x="34" y="50" width="32" height="30" rx="4" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="2"/>
  <ellipse cx="50" cy="84" rx="24" ry="10" fill="{C_GRAY}" stroke="{C_DARK}" stroke-width="2"/>
  <ellipse cx="50" cy="80" rx="20" ry="8" fill="{C_GRAY_L}"/>
""")

SVGS["nose"] = svg(f"""
  <ellipse cx="50" cy="44" rx="18" ry="28" fill="{C_SKIN}" stroke="{C_SKIN_D}" stroke-width="2.5"/>
  <path d="M34 68 Q50 76 66 68" stroke="{C_SKIN_D}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <circle cx="40" cy="66" r="6" fill="{C_SKIN_D}" opacity="0.5"/>
  <circle cx="60" cy="66" r="6" fill="{C_SKIN_D}" opacity="0.5"/>
""")

SVGS["stomach"] = svg(f"""
  <ellipse cx="50" cy="52" rx="32" ry="36" fill="{C_SKIN}" stroke="{C_SKIN_D}" stroke-width="2.5"/>
  <circle cx="50" cy="48" r="6" fill="{C_SKIN_D}" opacity="0.6" stroke="{C_SKIN_D}" stroke-width="1.5"/>
  <circle cx="50" cy="48" r="2.5" fill="{C_SKIN}"/>
  <path d="M30 60 Q50 72 70 60" stroke="{C_SKIN_D}" stroke-width="2.5" fill="none" stroke-linecap="round" opacity="0.5"/>
""")

# ════════════════════════════════════════════════════════════════
# CLOTHING
# ════════════════════════════════════════════════════════════════

SVGS["coat"] = svg(f"""
  <path d="M22 28 L10 44 L16 48 L26 40" fill="{C_GRAY_L}" stroke="{C_GRAY}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M78 28 L90 44 L84 48 L74 40" fill="{C_GRAY_L}" stroke="{C_GRAY}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M28 18 L22 28 L26 40 L38 36 L38 82 L62 82 L62 36 L74 40 L78 28 L72 18 L62 22 Q50 28 38 22 Z" fill="{C_GRAY_L}" stroke="{C_GRAY}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M50 22 L50 82" stroke="{C_GRAY}" stroke-width="2" stroke-dasharray="3,3"/>
  <circle cx="50" cy="40" r="3" fill="{C_GRAY}"/>
  <circle cx="50" cy="52" r="3" fill="{C_GRAY}"/>
  <circle cx="50" cy="64" r="3" fill="{C_GRAY}"/>
  <path d="M34 18 Q50 14 66 18" stroke="{C_GRAY_L}" stroke-width="8" fill="none"/>
""")

SVGS["hat"] = svg(f"""
  <ellipse cx="50" cy="54" rx="40" ry="12" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="2.5"/>
  <rect x="28" y="20" width="44" height="36" rx="6" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="2.5"/>
  <path d="M34 32 Q50 28 66 32" stroke="{C_AMBER_L}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <circle cx="50" cy="22" r="4" fill="{C_RED}"/>
""")

SVGS["jacket"] = SVGS["i_want_a_jacket"]

SVGS["pants"] = svg(f"""
  <rect x="18" y="16" width="64" height="30" rx="6" fill="{C_BLUE}" stroke="{C_BLUE_D}" stroke-width="2.5"/>
  <line x1="50" y1="16" x2="50" y2="46" stroke="{C_BLUE_D}" stroke-width="2.5"/>
  <rect x="18" y="42" width="28" height="44" rx="8" fill="{C_BLUE}" stroke="{C_BLUE_D}" stroke-width="2.5"/>
  <rect x="54" y="42" width="28" height="44" rx="8" fill="{C_BLUE}" stroke="{C_BLUE_D}" stroke-width="2.5"/>
  <rect x="36" y="18" width="28" height="10" rx="3" fill="{C_AMBER}" opacity="0.7"/>
  <circle cx="50" cy="23" r="3" fill="{C_AMBER_D}"/>
""")

SVGS["shoe"] = svg(f"""
  <path d="M14 60 Q14 44 28 44 L54 44 Q62 44 68 52 L82 52 Q90 52 90 62 L90 68 Q90 74 82 74 L20 74 Q14 74 14 68 Z" fill="{C_GRAY}" stroke="{C_DARK}" stroke-width="2.5"/>
  <path d="M14 64 L90 64" stroke="{C_DARK}" stroke-width="2" opacity="0.3"/>
  <path d="M28 44 L32 74" stroke="{C_DARK}" stroke-width="1.5" opacity="0.3"/>
  <ellipse cx="68" cy="52" rx="8" ry="6" fill="{C_GRAY_L}" opacity="0.5"/>
""")

SVGS["sock"] = svg(f"""
  <rect x="32" y="14" width="36" height="48" rx="6" fill="{C_RED}" stroke="#b91c1c" stroke-width="2.5"/>
  <path d="M32 56 Q16 62 16 74 Q16 86 36 86 L68 86 Q82 86 82 74 Q82 62 68 56" fill="{C_RED}" stroke="#b91c1c" stroke-width="2.5"/>
  <path d="M32 26 L68 26" stroke="white" stroke-width="4" stroke-linecap="round" opacity="0.5"/>
  <path d="M32 34 L68 34" stroke="white" stroke-width="4" stroke-linecap="round" opacity="0.5"/>
""")

SVGS["shirt"] = svg(f"""
  <path d="M30 18 L14 30 L22 40 L34 32 L34 78 L66 78 L66 32 L78 40 L86 30 L70 18 L62 24 Q50 28 38 24 Z" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2.5" stroke-linejoin="round"/>
  <path d="M50 24 L50 78" stroke="{C_BLUE}" stroke-width="2" stroke-dasharray="3,3"/>
  <path d="M38 18 Q50 14 62 18" fill="{C_SKIN}" stroke="{C_SKIN_D}" stroke-width="2"/>
""")

# ════════════════════════════════════════════════════════════════
# COLORS / DESCRIPTORS
# ════════════════════════════════════════════════════════════════

SVGS["red"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_RED}" stroke="#b91c1c" stroke-width="2.5"/>
  <text x="50" y="58" text-anchor="middle" font-size="16" font-weight="bold" fill="white" font-family="Arial, sans-serif">Red</text>
""")

SVGS["blue"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_BLUE}" stroke="{C_BLUE_D}" stroke-width="2.5"/>
  <text x="50" y="58" text-anchor="middle" font-size="16" font-weight="bold" fill="white" font-family="Arial, sans-serif">Blue</text>
""")

SVGS["green"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_GREEN}" stroke="{C_GREEN_D}" stroke-width="2.5"/>
  <text x="50" y="58" text-anchor="middle" font-size="16" font-weight="bold" fill="white" font-family="Arial, sans-serif">Green</text>
""")

SVGS["yellow"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_YELLOW}" stroke="{C_AMBER}" stroke-width="2.5"/>
  <text x="50" y="58" text-anchor="middle" font-size="18" font-weight="bold" fill="{C_AMBER_D}" font-family="Arial, sans-serif">Yellow</text>
""")

SVGS["orange"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_ORANGE}" stroke="{C_AMBER_D}" stroke-width="2.5"/>
  <text x="50" y="58" text-anchor="middle" font-size="14" font-weight="bold" fill="white" font-family="Arial, sans-serif">Orange</text>
""")

SVGS["purple"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_PURPLE}" stroke="#6d28d9" stroke-width="2.5"/>
  <text x="50" y="58" text-anchor="middle" font-size="14" font-weight="bold" fill="white" font-family="Arial, sans-serif">Purple</text>
""")

SVGS["black"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_DARK}" stroke="{C_GRAY}" stroke-width="2.5"/>
  <text x="50" y="58" text-anchor="middle" font-size="16" font-weight="bold" fill="white" font-family="Arial, sans-serif">Black</text>
""")

SVGS["white"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="white" stroke="{C_GRAY}" stroke-width="3"/>
  <text x="50" y="58" text-anchor="middle" font-size="16" font-weight="bold" fill="{C_GRAY}" font-family="Arial, sans-serif">White</text>
""")

SVGS["big"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2.5"/>
  <circle cx="36" cy="56" r="6" fill="{C_BLUE}"/>
  <circle cx="64" cy="42" r="20" fill="{C_BLUE}" opacity="0.85"/>
  <line x1="20" y1="62" x2="30" y2="62" stroke="{C_BLUE_D}" stroke-width="2" stroke-linecap="round"/>
  <text x="50" y="90" text-anchor="middle" font-size="9" font-weight="bold" fill="{C_BLUE_D}">BIG</text>
""")

SVGS["little"] = svg(f"""
  <circle cx="50" cy="50" r="38" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2.5"/>
  <circle cx="44" cy="52" r="18" fill="{C_BLUE}" opacity="0.85"/>
  <circle cx="68" cy="44" r="7" fill="{C_BLUE}"/>
  <text x="50" y="88" text-anchor="middle" font-size="9" font-weight="bold" fill="{C_BLUE_D}">LITTLE</text>
""")

SVGS["fast"] = svg(f"""
  <path d="M16 38 L70 38 L84 50 L70 62 L16 62 Q22 50 16 38Z" fill="{C_ORANGE}" stroke="{C_AMBER_D}" stroke-width="2"/>
  <line x1="28" y1="30" x2="12" y2="30" stroke="{C_ORANGE}" stroke-width="4" stroke-linecap="round"/>
  <line x1="28" y1="20" x2="18" y2="20" stroke="{C_ORANGE}" stroke-width="3" stroke-linecap="round" opacity="0.6"/>
  <line x1="28" y1="70" x2="12" y2="70" stroke="{C_ORANGE}" stroke-width="4" stroke-linecap="round"/>
  <circle cx="72" cy="50" r="8" fill="white" opacity="0.8"/>
""")

SVGS["slow"] = svg(f"""
  <circle cx="50" cy="50" r="32" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="3"/>
  <path d="M26 50 Q26 30 50 30 Q74 30 74 50 Q74 70 50 70 Q26 70 26 50" fill="none" stroke="{C_BLUE}" stroke-width="4" stroke-linecap="round" stroke-dasharray="8,4"/>
  <circle cx="26" cy="50" r="6" fill="{C_BLUE}"/>
""")

# ════════════════════════════════════════════════════════════════
# FOOD & DRINK
# ════════════════════════════════════════════════════════════════

SVGS["juice"] = svg(f"""
  <path d="M28 22 L32 82 Q32 88 40 88 L60 88 Q68 88 68 82 L72 22 Z" fill="{C_ORANGE}" stroke="{C_AMBER_D}" stroke-width="2.5"/>
  <path d="M29 40 L71 40 L70 82 Q70 86 60 86 L40 86 Q30 86 30 82 Z" fill="{C_ORANGE_L}" opacity="0.6"/>
  <ellipse cx="50" cy="22" rx="22" ry="3.5" fill="{C_AMBER_D}" opacity="0.7"/>
  <path d="M38 54 Q42 48 46 54 Q50 60 54 54" stroke="white" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.7"/>
  <path d="M68 32 L78 18" stroke="{C_GRAY_L}" stroke-width="3" stroke-linecap="round"/>
  <ellipse cx="80" cy="16" rx="6" ry="4" fill="{C_GREEN_L}"/>
""")

SVGS["candy"] = svg(f"""
  <circle cx="50" cy="54" r="26" fill="{C_ROSE}" stroke="#be123c" stroke-width="2.5"/>
  <path d="M30 34 Q50 46 70 34" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.6"/>
  <path d="M26 50 Q50 62 74 50" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.6"/>
  <line x1="50" y1="28" x2="50" y2="14" stroke="{C_GRAY}" stroke-width="5" stroke-linecap="round"/>
  <path d="M50 14 Q56 6 62 12" stroke="{C_GRAY}" stroke-width="4" fill="none" stroke-linecap="round"/>
""")

SVGS["carrot"] = svg(f"""
  <path d="M52 28 Q72 42 60 80 Q50 90 40 82 Q28 70 38 30 Z" fill="{C_ORANGE}" stroke="{C_AMBER_D}" stroke-width="2.5"/>
  <path d="M44 28 Q50 60 52 80" stroke="{C_AMBER_L}" stroke-width="2" fill="none" opacity="0.6"/>
  <path d="M52 28 Q42 12 36 8 Q44 16 48 28" fill="{C_GREEN}" stroke="{C_GREEN_D}" stroke-width="1.5"/>
  <path d="M52 28 Q56 10 62 6 Q56 16 52 28" fill="{C_GREEN}" stroke="{C_GREEN_D}" stroke-width="1.5"/>
  <path d="M52 28 Q66 16 70 10 Q62 20 52 28" fill="{C_GREEN}" stroke="{C_GREEN_D}" stroke-width="1.5"/>
""")

SVGS["fruit"] = svg(f"""
  <circle cx="38" cy="52" r="18" fill="{C_RED}" stroke="#b91c1c" stroke-width="2"/>
  <circle cx="62" cy="44" r="20" fill="{C_ORANGE}" stroke="{C_AMBER_D}" stroke-width="2"/>
  <circle cx="50" cy="64" r="16" fill="{C_GREEN}" stroke="{C_GREEN_D}" stroke-width="2"/>
  <path d="M50 18 Q44 10 36 14" stroke="{C_GREEN}" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M38 36 Q38 28 44 26" stroke="{C_GREEN}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
""")

SVGS["popcorn"] = svg(f"""
  <path d="M24 54 L30 84 L70 84 L76 54 Z" fill="{C_RED}" stroke="#b91c1c" stroke-width="2.5"/>
  <path d="M28 62 L72 62" stroke="white" stroke-width="3" opacity="0.4"/>
  <circle cx="36" cy="42" r="10" fill="{C_YELLOW_L}" stroke="{C_AMBER}" stroke-width="2"/>
  <circle cx="50" cy="36" r="12" fill="{C_YELLOW_L}" stroke="{C_AMBER}" stroke-width="2"/>
  <circle cx="64" cy="42" r="10" fill="{C_YELLOW_L}" stroke="{C_AMBER}" stroke-width="2"/>
  <circle cx="28" cy="52" r="8" fill="{C_YELLOW_L}" stroke="{C_AMBER}" stroke-width="2"/>
  <circle cx="72" cy="52" r="8" fill="{C_YELLOW_L}" stroke="{C_AMBER}" stroke-width="2"/>
""")

SVGS["pretzel"] = svg(f"""
  <path d="M50 82 Q20 82 20 60 Q20 44 36 44 Q52 44 50 58 Q48 72 38 72 Q28 72 28 60 Q28 48 38 44 Q50 36 64 44 Q80 52 80 68 Q80 82 60 82 Z" fill="none" stroke="{C_AMBER_D}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M38 38 Q50 22 62 38" fill="none" stroke="{C_AMBER_D}" stroke-width="10" stroke-linecap="round"/>
  <circle cx="44" cy="56" r="3" fill="white"/>
  <circle cx="56" cy="52" r="3" fill="white"/>
  <circle cx="50" cy="70" r="3" fill="white"/>
""")

SVGS["rice"] = svg(f"""
  <ellipse cx="50" cy="60" rx="34" ry="22" fill="{C_GRAY_L}" stroke="{C_GRAY}" stroke-width="2.5"/>
  <ellipse cx="50" cy="58" rx="30" ry="18" fill="white"/>
  <ellipse cx="38" cy="54" rx="5" ry="3" fill="{C_GRAY_L}" transform="rotate(-20 38 54)"/>
  <ellipse cx="52" cy="50" rx="5" ry="3" fill="{C_GRAY_L}" transform="rotate(10 52 50)"/>
  <ellipse cx="64" cy="56" rx="5" ry="3" fill="{C_GRAY_L}" transform="rotate(-15 64 56)"/>
  <ellipse cx="46" cy="64" rx="5" ry="3" fill="{C_GRAY_L}" transform="rotate(25 46 64)"/>
  <ellipse cx="60" cy="64" rx="5" ry="3" fill="{C_GRAY_L}" transform="rotate(-10 60 64)"/>
  <path d="M30 20 Q50 14 70 20" stroke="{C_GRAY}" stroke-width="3.5" fill="none" stroke-linecap="round"/>
""")

SVGS["waterjuice"] = SVGS["juice"]

SVGS["chips"] = svg(f"""
  <ellipse cx="44" cy="50" rx="24" ry="30" fill="{C_AMBER_L}" stroke="{C_AMBER}" stroke-width="2.5" transform="rotate(-20 44 50)"/>
  <ellipse cx="58" cy="46" rx="22" ry="28" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="2.5" transform="rotate(15 58 46)"/>
  <ellipse cx="50" cy="60" rx="20" ry="26" fill="{C_ORANGE}" stroke="{C_AMBER_D}" stroke-width="2.5" transform="rotate(-8 50 60)"/>
""")

SVGS["cookie"] = svg(f"""
  <circle cx="50" cy="50" r="36" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="2.5"/>
  <circle cx="38" cy="40" r="5" fill="{C_AMBER_D}"/>
  <circle cx="56" cy="36" r="5" fill="{C_AMBER_D}"/>
  <circle cx="62" cy="54" r="5" fill="{C_AMBER_D}"/>
  <circle cx="40" cy="58" r="5" fill="{C_AMBER_D}"/>
  <circle cx="52" cy="64" r="4" fill="{C_AMBER_D}"/>
""")

# ════════════════════════════════════════════════════════════════
# PREFERRED ITEMS
# ════════════════════════════════════════════════════════════════

SVGS["balloon"] = svg(f"""
  <circle cx="50" cy="40" r="32" fill="{C_RED}" stroke="#b91c1c" stroke-width="2.5"/>
  <path d="M34 24 Q28 32 32 40" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.5"/>
  <path d="M50 72 Q52 76 50 82 Q48 86 46 84 Q44 80 48 76" fill="{C_GRAY}" stroke="{C_DARK}" stroke-width="1.5"/>
  <line x1="50" y1="84" x2="50" y2="96" stroke="{C_GRAY}" stroke-width="2.5" stroke-linecap="round"/>
""")

SVGS["sand"] = svg(f"""
  <path d="M10 70 Q50 52 90 70 L90 90 L10 90 Z" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="2"/>
  <path d="M10 78 Q50 62 90 78" stroke="{C_AMBER_L}" stroke-width="2" fill="none" opacity="0.6"/>
  <ellipse cx="50" cy="72" rx="30" ry="8" fill="{C_AMBER_L}" opacity="0.5"/>
  <circle cx="30" cy="56" r="14" fill="{C_AMBER_L}" stroke="{C_AMBER}" stroke-width="2"/>
  <rect x="48" y="22" width="8" height="30" rx="2" fill="{C_RED}"/>
  <path d="M56 22 L74 34 L56 46 Z" fill="{C_RED}"/>
""")

SVGS["toygame"] = SVGS["game"]

SVGS["boat"] = svg(f"""
  <path d="M16 56 Q50 76 84 56 L80 68 Q50 86 20 68 Z" fill="{C_RED}" stroke="#b91c1c" stroke-width="2.5"/>
  <path d="M30 56 L30 28 L68 28 L68 56" fill="{C_BLUE_L}" stroke="{C_BLUE}" stroke-width="2"/>
  <path d="M30 28 L49 12 L49 28" fill="white" stroke="{C_GRAY}" stroke-width="1.5"/>
  <path d="M68 28 L68 42 L54 34 L68 28" fill="{C_AMBER}" stroke="{C_AMBER_D}" stroke-width="1.5"/>
  <path d="M8 68 Q50 80 92 68" stroke="{C_BLUE_L}" stroke-width="3" fill="none" stroke-linecap="round"/>
""")

# ════════════════════════════════════════════════════════════════
# QUICK PHRASES (aliases / compound)
# ════════════════════════════════════════════════════════════════

SVGS["too_loud_i_need_a_break"] = SVGS["too_loud"]
SVGS["no_i_dont_want_that"] = SVGS["i_dont_want_that"]
SVGS["help_me_im_frustrated"] = SVGS["help_me"]
SVGS["i_want_food"] = SVGS["eat"]
SVGS["i_want_apple"] = SVGS["fruit"]

# ════════════════════════════════════════════════════════════════
# DEFAULT FALLBACK (text label)
# ════════════════════════════════════════════════════════════════

def make_fallback(display_label, tab):
    tab_colors = {
        "core": (C_GREEN, C_GREEN_D),
        "actions": (C_GREEN, C_GREEN_D),
        "feelings": (C_YELLOW, C_AMBER_D),
        "people": (C_AMBER, C_AMBER_D),
        "things": (C_BLUE, C_BLUE_D),
        "more": (C_PURPLE, "#6d28d9"),
    }
    fill, stroke = tab_colors.get(tab, (C_GRAY, C_DARK))
    words = display_label.split()[:3]
    lines = []
    if len(words) == 1:
        lines = [(50, 58, words[0][:8])]
    elif len(words) == 2:
        lines = [(50, 52, words[0][:8]), (50, 66, words[1][:8])]
    else:
        lines = [(50, 44, words[0][:8]), (50, 58, words[1][:8]), (50, 72, words[2][:8])]
    text_els = "\n".join(
        f'<text x="{x}" y="{y}" text-anchor="middle" font-size="12" font-weight="bold" fill="{stroke}" font-family="Arial, sans-serif">{w}</text>'
        for (x, y, w) in lines
    )
    return svg(f"""
  <circle cx="50" cy="50" r="38" fill="{fill}" opacity="0.18"/>
  <circle cx="50" cy="50" r="32" fill="none" stroke="{fill}" stroke-width="3" stroke-dasharray="6,3"/>
  {text_els}
""")

# ─── MAIN OUTPUT ──────────────────────────────────────────────────────────────

def build_symbols_js(vocab_path, output_path):
    with open(vocab_path) as f:
        vocab = json.load(f)

    # Build symbol lookup
    sym_map = {}
    for s in vocab["symbols"]:
        sym_map[s["id"]] = s

    all_ids_needed = set(s["id"] for s in vocab["symbols"])

    lines = [
        "/**",
        " * AMIGA-AAC symbols.js — generated by generate_symbols.py",
        " * viewBox: 0 0 100 100, no background fill",
        " * Do not edit manually — re-run generate_symbols.py to regenerate.",
        " */",
        "",
        "export const SYMBOL_SVGS = {",
    ]

    found = 0
    fallback = 0

    for sym_id in sorted(all_ids_needed):
        sym = sym_map.get(sym_id, {})
        display = sym.get("display_label", sym_id)
        tab = sym.get("ui_tab", "more")

        # Also check svg_key alias
        svg_key = sym.get("svg_key")
        if sym_id in SVGS:
            svg_content = SVGS[sym_id]
            found += 1
        elif svg_key and svg_key in SVGS:
            svg_content = SVGS[svg_key]
            found += 1
        else:
            svg_content = make_fallback(display, tab)
            fallback += 1

        # Escape backticks and backslashes
        escaped = svg_content.replace("\\", "\\\\").replace("`", "\\`")
        lines.append(f"  \"{sym_id}\": `{escaped}`,")
        lines.append("")

    lines.append("};")
    lines.append("")
    lines.append("export default SYMBOL_SVGS;")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return found, fallback, len(all_ids_needed)


if __name__ == "__main__":
    import shutil
    from datetime import datetime

    # Paths relative to repo root (script lives in scripts/, outputs go to root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root  = os.path.dirname(script_dir)
    data_dir   = os.path.join(repo_root, "data")

    vocab_path  = os.path.join(repo_root, "vocabulary.json")
    output_path = os.path.join(repo_root, "symbols.js")

    os.makedirs(data_dir, exist_ok=True)

    datestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Back up existing outputs to data/ before overwriting
    for src_path, label in [(vocab_path, "vocabulary.json"), (output_path, "symbols.js")]:
        if os.path.exists(src_path):
            stem, ext = os.path.splitext(label)
            backup_name = f"{stem}_backup_{datestamp}{ext}"
            backup_path = os.path.join(data_dir, backup_name)
            shutil.copy2(src_path, backup_path)
            print(f"  Backed up {label} → data/{backup_name}")

    print(f"\nBuilding symbols.js from {vocab_path} ...")
    found, fallback_count, total = build_symbols_js(vocab_path, output_path)
    print(f"Done.")
    print(f"  Total symbols in vocab:   {total}")
    print(f"  Hand-crafted SVGs:        {found}")
    print(f"  Fallback (text label):    {fallback_count}")
    print(f"  Output: {output_path}")
    fsize = os.path.getsize(output_path)
    print(f"  File size: {fsize/1024:.1f} KB")
