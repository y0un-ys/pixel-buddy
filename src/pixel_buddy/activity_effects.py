"""Readable desk-level gestures for the seated Pixel Buddy illustrations.

The PNG character pose stays cute; these SVG shapes supply obvious contacts with
visible devices.  All coordinates share the 480x288 scene coordinate system.
"""
MODES = ("typing", "mouse", "watching", "gaming", "idle", "sleep")
EDGE = "#79627D"


def display_computer(pc, mode):
    """Watching uses a cinema-like monitor without modifying equipped items."""
    if mode == "watching" and pc == "laptop":
        return "desktop"
    return pc


def overlay_svg(mode="idle", frame=0, pc="laptop", species="cat"):
    mode = mode if mode in MODES else "idle"
    phase = max(0, int(frame)) % 4
    sx = 329 if pc == "laptop" else 342
    sy = 184 if pc == "laptop" else 173
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="480" height="288" viewBox="0 0 480 288">']
    out += ['<defs><linearGradient id="keygrad" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#FCF6FF"/><stop offset="1" stop-color="#C4B6DA"/></linearGradient></defs>']
    def add(*elements):
        out.extend(elements)
    if mode == "typing":
        # Compact keyboard directly under the illustration's EXISTING paws.
        # Do not add artificial arms/paws: the approved PNG already has two.
        # Left/right key groups alternate on successive 250ms ticks.
        add('<rect x="210" y="213" width="50" height="13" rx="4" fill="#9683AD" stroke="#715F86" stroke-width="1.5"/>',
            '<rect x="212" y="214" width="46" height="9" rx="3" fill="url(#keygrad)"/>')
        for i in range(6):
            x = 214 + i*7
            hot = (i >= 3) if phase % 2 == 0 else (i < 3)
            fill = "#F1A9C2" if hot else "#E4D9EC"
            y = 215 + (1 if hot else 0)
            add(f'<rect x="{x}" y="{y}" width="5.5" height="4" rx="1" fill="{fill}"/>')
        # Contact cues stay inside the keyboard; no floating hands or arrows.
        impact_x = 246 if phase % 2 == 0 else 222
        add(f'<ellipse cx="{impact_x}" cy="216" rx="5" ry="2" fill="#FFE5AA" opacity=".85"/>')
    elif mode == "mouse":
        # Compact mouse directly beside the character's original hand.
        # Mouse travels a few pixels horizontally; no drawn replacement arm.
        dx = (0, 3, 6, 3)[phase]
        add('<rect x="227" y="212" width="32" height="15" rx="5" fill="#DCCCE8" stroke="#B29DC4" stroke-width="1"/>',
            f'<ellipse cx="{241+dx}" cy="217" rx="7" ry="4.5" fill="#F8EEF9" stroke="#786C8B" stroke-width="1.6"/>')
        if phase == 2:
            add(f'<path d="M{240+dx} 210 l-2 -3 m6 3 l2 -3" fill="none" stroke="#E8A4C7" stroke-width="2" stroke-linecap="round"/>')
        cx = sx + (-6, -1, 4, -1)[phase]
        add(f'<path d="M{cx} {sy-6} v12 l4 -4 l4 7 l3 -2 l-4 -7 h6Z" fill="#FFF" stroke="#695D7D" stroke-width="1.2"/>')
    elif mode == "watching":
        # Large cinematic image inside the displayed PC's monitor, with
        # subtitles, pause/play control, progress bar and a tub of popcorn.
        if pc == "dual":
            add('<g transform="translate(278 160) scale(.92982456 .88095238) translate(-314 -157)">')
        add('<rect x="314" y="157" width="57" height="42" rx="5" fill="#282D55" stroke="#B9A5DA" stroke-width="2"/>',
            '<path d="M316 187 Q333 168 345 181 T369 166 L369 196 L316 196Z" fill="#957EB9"/>',
            '<circle cx="352" cy="173" r="8" fill="#FFF1CA" opacity=".75"/>',
            '<rect x="319" y="186" width="45" height="5" rx="2" fill="#EFE3F6" opacity=".70"/>',
            '<rect x="318" y="194" width="50" height="3" rx="1.5" fill="#514975"/>',
            f'<rect x="318" y="194" width="{8+phase*10}" height="3" rx="1.5" fill="#F3AFC4"/>',
            '<path d="M323 174 l0 12 l10 -6Z" fill="#FFF9EE"/>')
        if pc == "dual":
            add('</g>')
        add(
            '<path d="M240 222 l-5 -22 h29 l-5 22Z" fill="#ECA7B6" stroke="#9A718E" stroke-width="2"/>',
            '<path d="M238 204 h23" stroke="#FFF5D8" stroke-width="3"/>',
            '<circle cx="239" cy="198" r="5" fill="#FFF4C5"/>',
            '<circle cx="246" cy="195" r="6" fill="#FFF4C5"/>',
            '<circle cx="254" cy="199" r="5" fill="#FFF4C5"/>')
        # A kernel follows the existing lifting paw from the tub to the mouth,
        # disappears for the bite, then the same paw returns. No extra limb.
        if phase < 3:
            kernel_x, kernel_y = ((243, 196), (242, 188), (245, 177))[phase]
            add(f'<g id="popcorn-kernel" transform="translate({kernel_x} {kernel_y})">',
                '<circle cx="-2" cy="0" r="2.6" fill="#FFF4C5" stroke="#D9B46E" stroke-width=".8"/>',
                '<circle cx="1" cy="-2" r="2.7" fill="#FFF7DA"/>',
                '<circle cx="2" cy="1" r="2.5" fill="#FFE6A1"/>', '</g>')
        else:
            add('<path id="popcorn-bite" d="M247 174 l3 -2 m-1 7 l3 1" fill="none" stroke="#D9B46E" stroke-width="1.4" stroke-linecap="round"/>')
    elif mode == "gaming":
        add('<rect x="215" y="207" width="39" height="15" rx="8" fill="#9888AE" stroke="#6D5C83" stroke-width="3"/>',
            '<path d="M225 211 v8 m-4 -4 h8" stroke="#F8E9FF" stroke-width="2"/>',
            '<circle cx="244" cy="212" r="2" fill="#F7C5D8"/>',
            '<circle cx="249" cy="216" r="2" fill="#F2E5AB"/>')
    elif mode == "sleep":
        add('<circle cx="272" cy="126" r="21" fill="#FFF9FE" stroke="#DAC1E5" stroke-width="2"/>',
            '<text x="266" y="132" font-size="26" font-family="sans-serif" fill="#9F8AB8">z</text>')
    out.append("</svg>")
    return "".join(out)
