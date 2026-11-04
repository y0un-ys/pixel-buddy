"""Small animated foreground effects for the approved static chibi PNGs.

This module intentionally does not repaint the pet's face, fur, or paws.
Effects are positioned on the desk/computer so activity remains visible without
floating disconnected arms. SVG is portable between Qt and CairoSVG.
"""
from math import sin

MODES = ("typing", "mouse", "watching", "gaming", "idle", "sleep")


def overlay_svg(mode="idle", frame=0, pc="laptop"):
    """Produce a complete transparent 480x288 scene overlay."""
    mode = mode if mode in MODES else "idle"
    frame = max(0, int(frame))
    step = frame % 8
    sx = 325 if pc == "laptop" else (304 if pc == "dual" else 342)
    sy = 186 if pc == "laptop" else (179 if pc == "dual" else 173)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="480" height="288" viewBox="0 0 480 288">']
    if mode == "typing":
        # A four-step pastel typing rhythm anchored to the keyboard.
        for i in range(4):
            x = 273 + i * 13
            color = "#FFE8A2" if i == step % 4 else "#D7C6EB"
            out.append(f'<rect x="{x}" y="{224 - (i == step % 4) * 2}" width="9" height="3" rx="1.5" fill="{color}" opacity=".85"/>')
        out.append(f'<rect x="{sx-18}" y="{sy+9}" width="28" height="3" rx="1" fill="#B7EBCB" opacity=".75"/>')
        out.append(f'<rect x="{sx-18}" y="{sy+15}" width="{12+step*2}" height="3" rx="1" fill="#E8C5E8" opacity=".75"/>')
        out.append(f'<rect x="{sx+6+(step%3)*2}" y="{sy+15}" width="2" height="6" rx="1" fill="#FFF7B9"/>')
        if step in (1, 5):
            out.append('<path d="M264 197 l-5 -6 M273 193 l0 -7" fill="none" stroke="#E5ABC1" stroke-width="2.5" stroke-linecap="round"/>')
    elif mode == "mouse":
        cursor_x = sx + (step - 3) * 3
        cursor_y = sy + (step % 3 - 1) * 3
        out.append(f'<path d="M{cursor_x} {cursor_y} l0 14 l4 -4 l4 8 l3 -2 l-4 -8 l7 0 Z" fill="#FFFFFF" stroke="#7B658D" stroke-width="1.5"/>')
        out.append(f'<ellipse cx="{300 + step//2}" cy="222" rx="7" ry="3.5" fill="#C6B5D9" stroke="#82718D" stroke-width="1.5"/>')
        if step in (2, 6):
            out.append(f'<circle cx="{cursor_x+1}" cy="{cursor_y+2}" r="10" fill="none" stroke="#EEAFD1" stroke-width="2" opacity=".8"/>')
    elif mode == "watching":
        out.append(f'<rect x="{sx-20}" y="{sy+19}" width="42" height="3" rx="1.5" fill="#675C84"/>')
        out.append(f'<rect x="{sx-20}" y="{sy+19}" width="{5+step*5}" height="3" rx="1.5" fill="#FFE0A7"/>')
        out.append(f'<path d="M{sx-4} {sy-13} l0 20 l16 -10Z" fill="#FFF2DE" opacity=".85"/>')
        if step in (1, 5):
            out.append('<path d="M267 150 Q273 139 280 149" fill="none" stroke="#F3B5CC" stroke-width="3" stroke-linecap="round"/>')
    elif mode == "gaming":
        # Controller ONLY in gaming; do not cover the pet's own paws.
        out.append('<rect x="267" y="216" width="32" height="12" rx="6" fill="#8D7EAB" stroke="#625879" stroke-width="2"/>')
        out.append('<path d="M275 222 h8 m-4 -4 v8" stroke="#F1DEFF" stroke-width="2" stroke-linecap="round"/>')
        out.append('<circle cx="290" cy="220" r="2" fill="#F7B1C6"/><circle cx="294" cy="224" r="2" fill="#FFE49E"/>')
        out.append(f'<circle cx="{sx-9 + step*2}" cy="{sy-6 - abs(3-step)}" r="5" fill="#B6E3B4"/>')
        out.append(f'<path d="M{sx-17} {sy+8} h34" stroke="#F4DBAC" stroke-width="3" stroke-linecap="round"/>')
    elif mode == "idle":
        # Quiet breathing occurs on the pet image; no Z or sleep cues.
        if step in (0, 4):
            out.append('<path d="M263 145 Q268 136 273 144" fill="none" stroke="#E7C5DF" stroke-width="2" stroke-linecap="round" opacity=".65"/>')
    elif mode == "sleep":
        # Sleep is delayed until 150 seconds without observed interaction.
        out.append('<circle cx="278" cy="121" r="24" fill="#FFF8FC" stroke="#E8D3EF" stroke-width="2.5" opacity=".95"/>')
        out.append('<path d="M272 107 a9 9 0 1 0 12 13 a8 8 0 1 1 -12 -13" fill="#F5CDA6"/>')
        for i, size in enumerate((12, 17, 21)):
            y = 129 - i*12 + (step//2)%2*2
            x = 283 + i*13
            out.append(f'<text x="{x}" y="{y}" fill="#9F8DB9" font-size="{size}" font-family="sans-serif">z</text>')
    out.append("</svg>")
    return "".join(out)
