import tkinter as tk


# ###### МАЛЮВАННЯ ЗАКРУГЛЕНОГО ПРЯМОКУТНИКА / РИСОВАНИЕ ЗАКРУГЛЕННОГО ПРЯМОУГОЛЬНИКА ######
def draw_rounded_rectangle(
    canvas: tk.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    radius: float,
    fill: str,
    outline: str,
) -> int:
    """Малює на canvas закруглений прямокутник як згладжений полігон.
    Рисует на canvas закругленный прямоугольник как сглаженный полигон.
    """

    safe_radius = max(0.0, min(radius, abs(x2 - x1) / 2, abs(y2 - y1) / 2))
    points = [
        x1 + safe_radius,
        y1,
        x2 - safe_radius,
        y1,
        x2,
        y1,
        x2,
        y1 + safe_radius,
        x2,
        y2 - safe_radius,
        x2,
        y2,
        x2 - safe_radius,
        y2,
        x1 + safe_radius,
        y2,
        x1,
        y2,
        x1,
        y2 - safe_radius,
        x1,
        y1 + safe_radius,
        x1,
        y1,
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=20, fill=fill, outline=outline)
