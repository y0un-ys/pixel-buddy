"""Soft chibi companion artwork painted at logical 160x96 resolution.

Unlike the 4-frame pixel sprite legacy artwork, the character is drawn with
anti-aliased Qt vector paths, rounded outlines, cheeks, tiny paws and species
specific ears. Equipment and props are painted by the calling scene.
"""
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen

COLORS = {
    "cat": ("#F8C78D", "#FFF5E9", "#F2A6AF"),
    "dog": ("#D9AB81", "#FFF4E4", "#EDA6A7"),
    "bear": ("#BD947C", "#FFF0D9", "#EFABA6"),
    "fox": ("#EEA365", "#FFF0DD", "#EFA29E"),
    "rabbit": ("#F3E5EA", "#FFFAF7", "#EEA7BA"),
}
OUTLINE = "#805D70"
INK = "#44374B"


def draw_cozy_pet(p, species, shirt, outfit, y=0, step=0):
    """Draw the entire small seated pet; no square body/head seams."""
    species = species if species in COLORS else "cat"
    fur, cream, blush = COLORS[species]
    p.save()
    p.translate(0, y)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    def pen(color=OUTLINE, width=1.6):
        p.setPen(QPen(QColor(color), width))

    def ellipse(x, yy, w, h, fill, border=OUTLINE, stroke=1.5):
        pen(border, stroke)
        p.setBrush(QColor(fill))
        p.drawEllipse(QRectF(x, yy, w, h))

    def path(points, fill, stroke=1.5):
        shape = QPainterPath(QPointF(*points[0]))
        for point in points[1:]:
            shape.lineTo(QPointF(*point))
        shape.closeSubpath()
        pen(OUTLINE, stroke)
        p.setBrush(QColor(fill))
        p.drawPath(shape)

    # Tail behind the chair. Drawn early for natural depth.
    if species == "fox":
        ellipse(60, 53, 19, 15, fur)
        ellipse(72, 55, 7, 8, cream, cream, 0.5)
    elif species in ("cat", "dog"):
        ellipse(61, 58, 17, 10, fur)

    # Rounded feet and sweater body.
    ellipse(27, 66, 15, 10, fur)
    ellipse(52, 66, 14, 10, fur)
    ellipse(23, 49, 47, 26, shirt, OUTLINE, 1.7)
    ellipse(25, 54, 8, 16, shirt, shirt, 0.3)
    ellipse(61, 54, 8, 16, shirt, shirt, 0.3)
    if outfit == "suit":
        path([(43, 51), (49, 51), (46, 64)], "#FFF7F3", 0.7)
        path([(45, 52), (47, 52), (47, 60), (45, 60)], "#DD95A2", 0.7)
    elif outfit == "pajamas":
        for xx in (32, 43, 54):
            ellipse(xx, 63, 3, 3, "#FFE7AF", "#FFE7AF", 0.4)
    else:
        ellipse(39, 65, 12, 4, "#E0B2D5", "#E0B2D5", 0.3)

    # Species-specific small ears (not oversized triangles).
    if species == "cat":
        path([(25, 30), (26, 15), (34, 21), (40, 24)], fur)
        path([(54, 25), (62, 17), (68, 30), (60, 33)], fur)
        path([(29, 25), (29, 20), (35, 25)], blush, 0.6)
        path([(59, 25), (62, 21), (64, 26)], blush, 0.6)
    elif species == "fox":
        path([(23, 31), (27, 12), (40, 25)], fur)
        path([(54, 24), (66, 12), (70, 32)], fur)
        path([(28, 25), (30, 19), (36, 25)], blush, 0.6)
        path([(59, 25), (65, 19), (65, 27)], blush, 0.6)
    elif species == "bear":
        ellipse(22, 19, 17, 17, fur)
        ellipse(57, 19, 17, 17, fur)
        ellipse(27, 23, 7, 7, blush, blush, 0.5)
        ellipse(62, 23, 7, 7, blush, blush, 0.5)
    elif species == "dog":
        ellipse(17, 25, 16, 27, "#A77760")
        ellipse(63, 25, 16, 27, "#A77760")
    else:
        ellipse(28, 6, 12, 30, fur)
        ellipse(54, 6, 12, 30, fur)
        ellipse(32, 11, 4, 19, blush, blush, 0.5)
        ellipse(58, 11, 4, 19, blush, blush, 0.5)

    # Big round head, tiny cream muzzle, blush and eye sparkles.
    ellipse(20, 25, 54, 38, fur, OUTLINE, 1.8)
    ellipse(26, 39, 43, 22, cream, cream, 0.4)
    # Bright face patch for a calico-cat look.
    if species == "cat":
        ellipse(32, 29, 23, 15, cream, cream, 0.4)
    elif species == "fox":
        ellipse(30, 39, 36, 18, cream, cream, 0.4)
    for x in (35, 56):
        ellipse(x, 41, 5, 7, INK, INK, 0.2)
        ellipse(x + 1, 42, 1.8, 2.2, "#FFFFFF", "#FFFFFF", 0.3)
    ellipse(27, 49, 9, 5, blush, blush, 0.3)
    ellipse(63, 49, 9, 5, blush, blush, 0.3)
    ellipse(47, 50, 5, 3.7, "#986971", "#986971", 0.4)

    smile = QPainterPath(QPointF(49.5, 53.5))
    smile.cubicTo(47.0, 58.5, 43.5, 58.0, 42.0, 55.5)
    smile.moveTo(49.5, 53.5)
    smile.cubicTo(52.0, 58.5, 56.5, 58.0, 57.5, 55.5)
    p.setBrush(QColor("#00000000"))
    pen(OUTLINE, 1.0)
    p.drawPath(smile)

    # Little paws on the desk edge, independent of activity mode.
    if step % 2:
        ellipse(31, 60, 11, 8, cream, OUTLINE, 1.0)
        ellipse(54, 61, 10, 8, cream, OUTLINE, 1.0)
    else:
        ellipse(30, 61, 11, 8, cream, OUTLINE, 1.0)
        ellipse(55, 60, 10, 8, cream, OUTLINE, 1.0)
    p.restore()
