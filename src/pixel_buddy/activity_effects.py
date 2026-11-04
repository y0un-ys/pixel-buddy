"""Readable desk-level gestures for the seated Pixel Buddy illustrations.

The PNG character pose stays cute; these SVG shapes supply obvious contacts with
visible devices.  All coordinates share the 480x288 scene coordinate system.
"""
from html import escape

MODES = ("typing", "mouse", "watching", "gaming", "idle", "sleep")
EDGE = "#79627D"
FURS = {
    "cat": ("#F3BF88", "#FFF1DF"), "dog": ("#D6AD8E", "#FFEBD9"),
    "bear": ("#C59C85", "#F3DCC6"), "fox": ("#EEA36B", "#FFF0DD"),
    "rabbit": ("#EEE0E9", "#FFF9F7"),
}


def display_computer(pc, mode):
    """Watching uses a cinema-like monitor without modifying equipped items."""
    if mode == "watching" and pc == "laptop":
        return "desktop"
    return pc


def overlay_svg(mode="idle", frame=0, pc="laptop", species="cat"):
    mode = mode if mode in MODES else "idle"
    phase = max(0, int(frame)) % 4
    fur, paw = FURS.get(species, FURS["cat"])
    sx = 329 if pc == "laptop" else 342
    sy = 184 if pc == "laptop" else 173
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="480" height="288" viewBox="0 0 480 288">']
    out += ['<defs><linearGradient id="keygrad" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#FCF6FF"/><stop offset="1" stop-color="#C4B6DA"/></linearGradient></defs>']
    def add(*elements):
        out.extend(elements)
    def paw_at(x, y, radius=9):
        return (f'<ellipse cx="{x}" cy="{y}" rx="{radius}" ry="{radius*0.70}" '
                f'fill="{paw}" stroke="{EDGE}" stroke-width="2.4"/>')
    if mode == "typing":
        # A clearly identifiable, full-width keyboard sits ON the desk, even
        # when the laptop screen hides most of its original shallow base.
        add('<rect x="245" y="218" width="100" height="17" rx="5" fill="#9787AF" stroke="#78678B" stroke-width="2"/>',
            '<rect x="248" y="219" width="94" height="12" rx="4" fill="url(#keygrad)"/>')
        for row in range(2):
            for i in range(10):
                x, y = 254+i*8.5, 221+row*5
                hot = (i//3 == phase//2 and row == phase%2)
                fill = "#F5B3C9" if hot else "#E3D8ED"
                add(f'<rect x="{x}" y="{y}" width="6.3" height="3.5" rx="1" fill="{fill}" stroke="#B5A5CB" stroke-width=".4"/>')
        # Both arms originate near the body: short downstroke alternates L/R.
        # frames: left down / neutral / right down / neutral.
        left_y = (220, 208, 210, 208)[phase]
        right_y = (207, 208, 220, 208)[phase]
        add(f'<path d="M227 203 Q244 207 261 {left_y-3}" fill="none" stroke="{EDGE}" stroke-width="12" stroke-linecap="round"/>',
            f'<path d="M227 203 Q244 207 261 {left_y-3}" fill="none" stroke="{fur}" stroke-width="8" stroke-linecap="round"/>',
            f'<path d="M236 206 Q267 204 302 {right_y-3}" fill="none" stroke="{EDGE}" stroke-width="12" stroke-linecap="round"/>',
            f'<path d="M236 206 Q267 204 302 {right_y-3}" fill="none" stroke="{fur}" stroke-width="8" stroke-linecap="round"/>',
            paw_at(262, left_y), paw_at(303, right_y))
        if phase == 0:
            add('<path d="M262 229 l-2 5 m-5 -6 l-4 4" stroke="#E99DBB" stroke-width="2" stroke-linecap="round"/>')
        elif phase == 2:
            add('<path d="M303 229 l2 5 m5 -6 l4 4" stroke="#E99DBB" stroke-width="2" stroke-linecap="round"/>')
    elif mode == "mouse":
        # One paw stays planted; the other moves linearly 10px across a mousepad.
        dx = (0, 5, 10, 5)[phase]
        add('<rect x="277" y="219" width="63" height="17" rx="6" fill="#D9CBE6" stroke="#AD97C3" stroke-width="1.6"/>',
            '<rect x="257" y="221" width="26" height="8" rx="3" fill="#E3D4E9" stroke="#B29EC4" stroke-width="1"/>',
            '<ellipse cx="'+str(310+dx)+'" cy="226" rx="9" ry="5" fill="#F6E6FB" stroke="#796B8E" stroke-width="2"/>',
            f'<path d="M228 203 Q267 204 {310+dx} 222" fill="none" stroke="{EDGE}" stroke-width="13" stroke-linecap="round"/>',
            f'<path d="M228 203 Q267 204 {310+dx} 222" fill="none" stroke="{fur}" stroke-width="9" stroke-linecap="round"/>',
            paw_at(310+dx, 220, 9),
            paw_at(260, 218, 8))
        if phase == 2:
            add(f'<path d="M{308+dx} 210 l-3 -5 m9 5 l3 -5" stroke="#EBA8CC" stroke-width="2.5" stroke-linecap="round"/>')
        # Screen cursor follows a small horizontal sweep, not circular motion.
        cx = sx + (-8, -2, 4, -2)[phase]
        add(f'<path d="M{cx} {sy-6} v12 l4 -4 l4 7 l3 -2 l-4 -7 h6Z" fill="#FFF" stroke="#695D7D" stroke-width="1.2"/>')
    elif mode == "watching":
        # Large cinematic image inside the displayed PC's monitor, with
        # subtitles, pause/play control, progress bar and a tub of popcorn.
        add('<rect x="314" y="157" width="57" height="42" rx="5" fill="#282D55" stroke="#B9A5DA" stroke-width="2"/>',
            '<path d="M316 187 Q333 168 345 181 T369 166 L369 196 L316 196Z" fill="#957EB9"/>',
            '<circle cx="352" cy="173" r="8" fill="#FFF1CA" opacity=".75"/>',
            '<rect x="319" y="186" width="45" height="5" rx="2" fill="#EFE3F6" opacity=".70"/>',
            '<rect x="318" y="194" width="50" height="3" rx="1.5" fill="#514975"/>',
            f'<rect x="318" y="194" width="{8+phase*10}" height="3" rx="1.5" fill="#F3AFC4"/>',
            '<path d="M323 174 l0 12 l10 -6Z" fill="#FFF9EE"/>',
            '<path d="M270 222 l-5 -22 h29 l-5 22Z" fill="#ECA7B6" stroke="#9A718E" stroke-width="2"/>',
            '<path d="M268 204 h23" stroke="#FFF5D8" stroke-width="3"/>',
            '<circle cx="269" cy="198" r="5" fill="#FFF4C5"/>',
            '<circle cx="276" cy="195" r="6" fill="#FFF4C5"/>',
            '<circle cx="284" cy="199" r="5" fill="#FFF4C5"/>')
        if phase in (1, 3):
            add('<text x="279" y="147" fill="#E69DBA" font-size="18" font-family="sans-serif">♥</text>')
    elif mode == "gaming":
        add('<rect x="271" y="214" width="45" height="15" rx="8" fill="#9888AE" stroke="#6D5C83" stroke-width="3"/>',
            '<path d="M282 219 v8 m-4 -4 h8" stroke="#F8E9FF" stroke-width="2"/>',
            '<circle cx="303" cy="221" r="2" fill="#F7C5D8"/>',
            '<circle cx="309" cy="225" r="2" fill="#F2E5AB"/>')
        add(paw_at(274, 217+(-2, 2, -2, 2)[phase]),
            paw_at(312, 217+(2, -2, 2, -2)[phase]))
    elif mode == "sleep":
        add('<circle cx="272" cy="126" r="21" fill="#FFF9FE" stroke="#DAC1E5" stroke-width="2"/>',
            '<text x="266" y="132" font-size="26" font-family="sans-serif" fill="#9F8AB8">z</text>')
    out.append("</svg>")
    return "".join(out)
