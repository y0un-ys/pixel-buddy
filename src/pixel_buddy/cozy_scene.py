"""Cozy 3/4-side desktop companion scene.

An independent, pure-Python SVG scene builder. Every equipment/animal/mode
uses the same coordinates and layering; no detached legacy paw rectangles.
QtSvg consumes the string in BuddyScene, and CairoSVG can render previews.
"""
from html import escape

ANIMALS = ("cat", "dog", "bear", "fox", "rabbit")
MODES = ("typing", "mouse", "watching", "gaming", "idle")
PALETTES = {
    "cat": ("#F6BF84", "#FFF7EA", "#EF9FAA"),
    "dog": ("#DDB58F", "#FFEFDB", "#ECA3A5"),
    "bear": ("#C69E83", "#F5DDC6", "#E89CA7"),
    "fox": ("#EBA367", "#FFF0DB", "#ECA4A5"),
    "rabbit": ("#F3E6EC", "#FFF9F7", "#EAA5BD"),
}
EDGE = "#765D7E"
S = []

def _ellipse(cx, cy, rx, ry, fill, stroke=EDGE, sw=2.7, extra=""):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

def _rect(x, y, w, h, r, fill, stroke=EDGE, sw=2, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

def _path(d, fill, stroke=EDGE, sw=2.7, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'

def scene_svg(species="cat", mode="typing", pc="laptop", prop="", desk="", outfit="hoodie", hat="", frame=0, room=False, reaction=""):
    """Return complete 480x288 transparent illustration for QtSvgRenderer."""
    species = species if species in PALETTES else "cat"
    mode = mode if mode in MODES else "idle"
    fur, cream, pink = PALETTES[species]
    beat = int(frame) % 4
    wobble = (0, 1, 0, -1)[beat]
    shirt = {"hoodie":"#9CB1E7","pajamas":"#D6AFE6","suit":"#7285B2"}.get(outfit,"#9CB1E7")
    wood = {"oak_desk":"#E6AC74","pink_desk":"#EFBDD6","gaming_desk":"#91A7C9"}.get(desk,"#E6B38B")
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="480" height="288" viewBox="0 0 480 288">']
    out += ['<defs><linearGradient id="wood" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#FFF0D7"/><stop offset="1" stop-color="'+wood+'"/></linearGradient>',
            '<linearGradient id="screen" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#A79ACF"/><stop offset="1" stop-color="#615986"/></linearGradient>',
            '<linearGradient id="chair" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#D5B5DE"/><stop offset="1" stop-color="#9986B7"/></linearGradient></defs>']
    # A floating little floor and a chair behind the animal, not a flat pixel island.
    out += [_ellipse(245,258,216,20,"#EEE2F5","#D0BDEB",2.8),
            _ellipse(245,262,185,8,"#F9F0FA","#F9F0FA",0)]
    if room:
        out += [_rect(8,5,464,270,20,"#FFF6EE","#E9D7E6",2),
                _rect(18,15,78,75,8,"#D7E7EF","#D7C4DC",3),
                _rect(24,21,66,63,6,"#EBF8FF","#FFFFFF",1)]
    out += ['<!--PET-CHAIR-START-->']
    out += [_rect(78,141,83,106,25,"url(#chair)","#75648D",4),
            _ellipse(119,227,48,13,"#9A83B2","#76638E",3),
            _path("M102 232 Q110 252 106 258 L123 258 Q127 247 125 231Z","#88739D","#76638E",3)]
    out += ['<!--PET-CHAIR-END-->']
    # Table legs: always beneath the tabletop and its objects.
    out += [_rect(168,228,16,32,4,"#C4937E","#9B737E",3),
            _rect(423,228,16,32,4,"#C4937E","#9B737E",3)]
    out += ['<!--PET-BODY-START-->']
    # Tail behind body, expressive but never detached.
    if species == "fox":
        out += [_path("M143 211 Q109 184 90 207 Q87 232 125 237 Q141 234 150 225Z",fur,EDGE,3),
                _path("M93 208 Q100 194 111 204 L123 218 Q105 227 93 208Z",cream,"none",0)]
    elif species in ("cat","dog"):
        out += [_path("M143 219 C117 228 107 211 116 198 C125 189 140 204 148 211Z",fur,EDGE,3)]
    elif species == "rabbit":
        out += [_ellipse(130,215,14,13,cream,EDGE,3)]
    # Rounded, petite body in a real seated pose.
    out += [_ellipse(181,204,59,42,shirt,EDGE,3.5),
            _ellipse(155,232,24,14,fur,EDGE,3),
            _ellipse(199,232,23,13,fur,EDGE,3)]
    if outfit == "hoodie":
        out += [_path("M153 225 Q182 232 208 218","none","#879BD4",3),
                _ellipse(191,225,12,4,"#BBD0EF","#BBD0EF",0)]
    elif outfit == "pajamas":
        out += [_ellipse(164,209,5,5,"#FFEAD5","none",0),_ellipse(183,216,5,5,"#FFEAD5","none",0)]
    else:
        out += [_path("M185 182 L198 211 L185 224 L174 209Z","#F6F1F4","none",0),
                _path("M186 192 L192 205 L187 212Z","#EBA8B4","none",0)]
    # Ears first, head in front. Not an oversized monkey muzzle.
    if species == "cat":
        out += [_path("M144 131 L150 98 Q164 99 171 123Z",fur,EDGE,4),
                _path("M219 119 Q230 97 243 104 L244 141Z",fur,EDGE,4),
                _path("M153 121 L156 108 L166 124Z",pink,"none",0),
                _path("M231 121 L238 109 L239 130Z",pink,"none",0)]
    elif species == "fox":
        out += [_path("M139 131 L149 92 L172 125Z",fur,EDGE,4),
                _path("M214 120 L246 94 L244 144Z",fur,EDGE,4),
                _path("M151 120 L154 104 L165 124Z",pink,"none",0),
                _path("M227 121 L240 106 L238 132Z",pink,"none",0)]
    elif species == "bear":
        out += [_ellipse(152,119,22,22,fur,EDGE,4),
                _ellipse(226,123,22,22,fur,EDGE,4),
                _ellipse(153,117,10,11,pink,"none",0),
                _ellipse(226,121,10,11,pink,"none",0)]
    elif species == "dog":
        out += [_ellipse(142,150,22,40,"#B98673",EDGE,4),
                _ellipse(247,154,18,38,"#B98673",EDGE,4)]
    elif species == "rabbit":
        out += [_ellipse(158,89,16,45,fur,EDGE,4),
                _ellipse(218,87,16,47,fur,EDGE,4),
                _ellipse(158,89,7,32,pink,"none",0),
                _ellipse(218,88,7,33,pink,"none",0)]
    # The head is deliberately wider than the body and faces right in 3/4 view.
    out += [_path("M135 155 C135 117 157 111 194 113 C234 111 254 132 256 161 C258 190 242 206 210 210 C173 212 141 195 135 173Z",fur,EDGE,4)]
    # A flat white facial patch instead of protruding round monkey muzzle.
    if species == "cat":
        out += [_path("M180 116 Q210 111 229 127 L232 159 Q214 153 204 143 Q194 135 181 141Z",cream,"none",0)]
    elif species == "fox":
        out += [_path("M158 164 Q201 188 253 157 Q249 205 211 207 Q162 208 158 164Z",cream,"none",0)]
    else:
        out += [_path("M160 173 Q183 183 202 166 Q220 152 250 164 Q251 199 213 207 Q170 208 160 173Z",cream,"none",0)]
    # Expressive eyes toward monitor, small nose and cheeks.
    out += [_ellipse(195,159,4.6,7,"#483A52","#483A52",0),
            _ellipse(237,157,4.8,7,"#483A52","#483A52",0),
            _ellipse(195,156,1.8,2.6,"#FFFFFF","none",0),
            _ellipse(237,154,1.8,2.6,"#FFFFFF","none",0),
            _ellipse(177,177,13,7,pink,"none",0,'opacity=".75"'),
            _ellipse(244,175,10,6,pink,"none",0,'opacity=".75"'),
            _ellipse(245,168,4,3.5,"#956878","none",0),
            _path("M242 174 Q246 180 250 174","none","#956878",2)]
    if species == "cat":
        out += [_path("M184 143 Q196 146 206 142","none","#E7B6A0",3)]
    # Ribbon/hat anchored to the actual head, not old pixel coordinates.
    if hat == "ribbon":
        out += [_path("M207 122 Q194 109 188 120 Q196 129 207 125 Q221 113 227 122 Q218 132 207 125Z","#EF9EC0","#9F728F",2),
                _ellipse(207,125,5,5,"#FFE1B8","#9F728F",1)]
    elif hat == "cat_ears" and species not in ("cat","fox"):
        out += [_path("M160 117 L168 99 L184 117Z","#A78DA8",EDGE,2),
                _path("M212 117 L228 99 L239 123Z","#A78DA8",EDGE,2)]
    elif hat == "bunny_ears" and species != "rabbit":
        out += [_ellipse(184,98,9,27,"#FFF0F4",EDGE,2),
                _ellipse(204,97,9,27,"#FFF0F4",EDGE,2)]
    out += ['<!--PET-BODY-END-->', '<!--SCENE-FOREGROUND-->']
    # Desk: believable overlap across belly, with paws on TOP afterward.
    out += [_rect(148,223,313,15,8,"url(#wood)","#9B7183",3.2),
            _path("M152 230 L457 230","none","#FFF1DB",2)]
    # Computer display on the right; no controller unless actually gaming.
    if pc == "laptop":
        out += [_path("M275 219 L293 159 Q296 155 303 155 L368 155 Q373 155 372 164 L357 219Z","#A995C7",EDGE,4),
                _path("M300 163 L362 163 L348 210 L286 210Z","url(#screen)","#CFC2E6",2),
                _path("M273 220 L357 220 L372 226 L269 226Z","#C3AFD8",EDGE,2.5),
                _ellipse(328,182,11,10,"#E9E4FA","none",0)]
        # Pet paw print on laptop.
        out += [_ellipse(324,176,3,3,"#A696C7","none",0),_ellipse(331,175,3,3,"#A696C7","none",0),
                _ellipse(338,179,3,3,"#A696C7","none",0),_ellipse(332,186,6,5,"#A696C7","none",0)]
    else:
        positions = [(306,146,72,59)] if pc != "dual" else [(271,152,67,54),(346,145,74,61)]
        for x, yy, w, h in positions:
            out += [_rect(x,yy,w,h,8,"url(#screen)",EDGE,4),
                    _rect(x+7,yy+8,w-14,h-17,4,"#4A416E","#BBB2DF",1),
                    _rect(x+15,yy+18,w-31,5,2,"#C5B1E7","none",0),
                    _rect(x+15,yy+31,w-38,4,2,"#9DCAB0","none",0),
                    _rect(x+w/2-3,yy+h,6,16,2,"#8E81AA",EDGE,1),
                    _rect(x+w/2-17,yy+h+14,34,5,2,"#BFB2D3",EDGE,1)]
        if pc != "dual":
            out += [_rect(393,165,20,45,5,"#ACA0C3",EDGE,3),
                    _rect(399,174,8,3,1,"#DDD6EC","none",0)]
    # Screen action cues.
    if mode == "watching":
        out += [_rect(317,189,21,4,2,"#F5B2B9","none",0)]
    elif mode == "mouse":
        out += [_path("M335 179 l0 11 l5 -3 l3 6 l3 -2 l-4 -6 l6 0Z","#FFF8F0",EDGE,1)]
    elif mode == "gaming":
        out += [_ellipse(339,190,6,6,"#F4CE90","none",0)]
    # Decor is centered ON THE DESK. Never hangs beyond x=461.
    if prop == "plant":
        out += [_rect(426,203,25,24,4,"#D8A28B","#9D7588",2.5),
                _ellipse(432,193,10,15,"#98BF86","#5E897D",2),
                _ellipse(443,191,11,16,"#A6CE96","#5E897D",2),
                _ellipse(437,182,8,16,"#B8D7A0","#5E897D",2)]
    elif prop == "lamp":
        out += [_rect(427,221,29,5,2,"#C6B4D8",EDGE,2),
                _path("M438 222 L441 182 L451 166","none","#A79AC3",5),
                _path("M437 163 Q454 148 465 169 L458 181 L432 173Z","#D0B2D9",EDGE,2),
                _ellipse(450,175,6,5,"#FFE8A9","none",0)]
    elif prop == "plushie":
        out += [_ellipse(443,211,13,14,"#D9AF91",EDGE,2),
                _ellipse(434,202,6,7,"#D9AF91",EDGE,2),
                _ellipse(453,202,6,7,"#D9AF91",EDGE,2),
                _ellipse(439,210,2,2,"#55465F","none",0),
                _ellipse(448,210,2,2,"#55465F","none",0)]
    out += ['<!--PET-PAWS-START-->']
    # Forepaws are continuous with arms, and their ends always meet the desk.
    shift = wobble * 2 if mode in ("typing","mouse","gaming") else 0
    out += [_path("M212 197 Q225 207 242 217 L252 220 Q259 223 259 216 Q256 210 245 210 Q236 196 226 191Z",fur,EDGE,3)]
    if mode == "typing":
        out += [_ellipse(264+shift,218,13,8,cream,EDGE,2.3),
                _ellipse(289-shift,219,12,7,cream,EDGE,2.3),
                _rect(264,222,57,5,2,"#B9A5CE",EDGE,1),
                _rect(271+(beat*9),221,7,2,1,"#F6A9BD","none",0)]
    elif mode == "mouse":
        out += [_ellipse(281+shift,218,15,8,cream,EDGE,2.3),
                _ellipse(257,218,10,7,cream,EDGE,2),
                _ellipse(303,223,8,3,"#B8A6CF",EDGE,1)]
    elif mode == "gaming":
        out += [_path("M260 216 Q257 209 270 208 L291 208 Q307 208 303 222 Q295 226 289 217 L275 217 Q267 226 260 216Z","#75688C",EDGE,2.5),
                _ellipse(265,215,11,7,cream,EDGE,2),_ellipse(298,215,11,7,cream,EDGE,2),
                _rect(276,214,9,2,1,"#DCD5EC","none",0),
                _ellipse(296,211,2,2,pink,"none",0)]
    elif mode == "watching":
        out += [_rect(290,201,21,24,3,"#E49AA9",EDGE,2),
                _ellipse(300,198,12,6,"#FFF3C6","none",0),
                _ellipse(273,218,12,8,cream,EDGE,2),
                _ellipse(295,191+wobble,10,7,cream,EDGE,2)]
    else:
        out += [_ellipse(265,217,13,8,cream,EDGE,2),
                _ellipse(286,219,11,7,cream,EDGE,2)]
    out += ['<!--PET-PAWS-END-->']
    if mode == "idle":
        out += ['<text x="260" y="132" font-size="25" font-family="sans-serif" fill="#B39BC8">z</text>']
    if reaction:
        mark = {"happy":"♥","sleep":"z","curious":"?","coffee":"♡","stretch":"!","snack":"♪"}.get(reaction,"♥")
        out += [_ellipse(276,119,20,17,"#FFF9FD","#D9BDD9",2),
                f'<text x="267" y="126" font-size="19" fill="#E89CB9" font-family="sans-serif">{escape(mark)}</text>']
    out += ["</svg>"]
    return "".join(out)


def scene_illustration_layers(**kwargs):
    """Return (background, foreground) SVGs for the illustrated companion.

    Chair, body and legacy SVG paws are suppressed together; the PNG character
    includes a chair and hands. The desk and equipment render in front.
    """
    import re

    markup = scene_svg(**kwargs)
    for name in ("CHAIR", "BODY", "PAWS"):
        markup, removed = re.subn(
            r"<!--PET-" + name + r"-START-->.*?<!--PET-" + name + r"-END-->",
            "",
            markup,
            count=1,
            flags=re.DOTALL,
        )
        if removed != 1:
            raise ValueError("Missing scene illustration layer: " + name)

    background, foreground = markup.split("<!--SCENE-FOREGROUND-->", 1)
    header = background[:background.index(">") + 1]
    defs = re.search(r"<defs>.*?</defs>", background, flags=re.DOTALL)
    if defs is None:
        raise ValueError("Scene SVG gradient definitions missing")
    return background + "</svg>", header + defs.group(0) + foreground
