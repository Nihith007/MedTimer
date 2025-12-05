
import base64
import streamlit as st
import streamlit.components.v1 as components

# IMPORTANT: install `svg-turtle` (pip install svg-turtle)
from svg_turtle import SvgTurtle  # SaVaGe Turtle
# In recent versions, SvgTurtle exposes .to_svg() to get the SVG string without writing a file.

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="MedTimer Turtle UI", layout="wide")

# ---------- PALETTE (replace with your exact hex codes) ----------
PALETTE = {
    # Backgrounds
    "page_bg": "#EAF2FF",     # very light blue page background
    "card_bg": "#FFFFFF",     # white card
    "card_border": "#CBE9DD", # soft green border
    # Text (if you overlay text via HTML/CSS)
    "text": "#2E3748",
    "muted": "#8A94A6",
    # Accents
    "success": "#27AE60",     # green
    "success_bg": "#E7F8EF",  # light green chip background
    "primary": "#2D79FF",     # button blue
    "divider": "#E8EDF5",
    "gauge_orange": "#FF7A00",
    "gauge_ring": "#E9ECF2",
    "nav_bg": "#FFFFFF",
    "nav_icon": "#7785A1",
}

# ---------- DEVICE PRESETS ----------
DEVICES = {
    "Desktop (1280×800)": (1280, 800),
    "Mobile (375×812)": (375, 812),  # typical iPhone-ish portrait
}

device_label = st.sidebar.selectbox("Device/Canvas size", list(DEVICES.keys()), index=0)
W, H = DEVICES[device_label]

screen = st.sidebar.radio("Screen", ["Home", "Score"], index=0)
st.sidebar.write("Tip: replace PALETTE hex values to match your exact colors.")

# ---------- SVG MOUNT ----------
def show_svg(svg_text: str, width: int, height: int, scrolling: bool = False):
    """
    Renders an SVG string in Streamlit.
    Uses a data URL to avoid file I/O.
    """
    b64 = base64.b64encode(svg_text.encode("utf-8")).decode("utf-8")
    html = f"""
    <div style="display:flex; justify-content:center;">
      data:image/svg+xml;base64,{b64}
    </div>
    """
    components.html(html, width=width+40, height=height+40, scrolling=scrolling)

# ---------- COORDINATE HELPERS ----------
def to_turtle_xy_canvas(x_px: float, y_px: float, canvas_w: int, canvas_h: int):
    """
    Convert top-left canvas coordinates (x_px, y_px) to turtle coordinates (center-origin).
    Turtle coords: (0,0) center, +x right, +y up.
    Canvas coords: (0,0) top-left, +x right, +y down.
    """
    tx = x_px - canvas_w / 2
    ty = canvas_h / 2 - y_px
    return tx, ty

def goto_top_left(t: SvgTurtle, x: float, y: float, canvas_w: int, canvas_h: int):
    tx, ty = to_turtle_xy_canvas(x, y, canvas_w, canvas_h)
    t.penup()
    t.goto(tx, ty)
    t.pendown()

# ---------- SHAPES ----------
def rounded_rect(t: SvgTurtle, x: float, y: float, w: float, h: float, r: float,
                 stroke: str, fill: str, stroke_width: float, canvas_w: int, canvas_h: int):
    """
    Draw a rounded rectangle at top-left (x,y).
    Uses four quarter-circle arcs (t.circle) with straight segments between.
    """
    # Start slightly inset to draw the top edge from left to right:
    start_x = x + r
    start_y = y
    goto_top_left(t, start_x, start_y, canvas_w, canvas_h)
    t.pencolor(stroke)
    t.fillcolor(fill)
    t.pensize(stroke_width)
    t.begin_fill()

    # Heading east for the top edge
    t.setheading(0)
    t.forward(w - 2*r)      # top straight
    t.circle(r, 90)         # top-right corner
    t.forward(h - 2*r)      # right straight
    t.circle(r, 90)         # bottom-right corner
    t.forward(w - 2*r)      # bottom straight
    t.circle(r, 90)         # bottom-left corner
    t.forward(h - 2*r)      # left straight
    t.circle(r, 90)         # top-left corner to close
    t.end_fill()

def circle_ring(t: SvgTurtle, cx: float, cy: float, radius: float, thickness: float,
                color: str, canvas_w: int, canvas_h: int, start_heading: float = 0, extent: float = 360):
    """
    Draw a ring or circular arc with a given thickness.
    """
    # Turtle draws circles from the current position with radius measured from center.
    # Move to the start point: center above the circle by radius.
    start_x = cx
    start_y = cy - radius
    goto_top_left(t, start_x, start_y, canvas_w, canvas_h)
    t.pencolor(color)
    t.pensize(thickness)
    t.fillcolor("")  # no fill
    t.setheading(start_heading)
    t.circle(radius, extent)

def pill_chip(t: SvgTurtle, x: float, y: float, w: float, h: float, color_bg: str, color_border: str,
              label_width: float, canvas_w: int, canvas_h: int):
    """
    A simple capsule to represent '✓ Taken' chip (shape only).
    """
    rounded_rect(t, x, y, w, h, r=h/2, stroke=color_border, fill=color_bg, stroke_width=1.0,
                 canvas_w=canvas_w, canvas_h=canvas_h)
    # A tiny green circle tick on left
    tick_r = h * 0.35
    cx = x + h/2 + tick_r/2
    cy = y + h/2
    # draw small filled circle
    goto_top_left(t, cx, cy - tick_r/2, canvas_w, canvas_h)
    t.pencolor(PALETTE["success"])
    t.fillcolor(PALETTE["success"])
    t.begin_fill()
    t.circle(tick_r/2)
    t.end_fill()

def button_primary(t: SvgTurtle, x: float, y: float, w: float, h: float, canvas_w: int, canvas_h: int):
    rounded_rect(t, x, y, w, h, r=10, stroke=PALETTE["primary"], fill=PALETTE["primary"],
                 stroke_width=1.0, canvas_w=canvas_w, canvas_h=canvas_h)

# ---------- SCREENS ----------
def draw_home_svg(canvas_w: int, canvas_h: int) -> str:
    """
    Draws the "Today's Medicines" card + summary chips on a light-blue page.
    Pure turtle (SVG) for shapes; text can be layered via Streamlit markdown if needed.
    """
    t = SvgTurtle(canvas_w, canvas_h)

    # Page background
    rounded_rect(t, 0, 0, canvas_w, canvas_h, r=0,
                 stroke=PALETTE["page_bg"], fill=PALETTE["page_bg"], stroke_width=0.0,
                 canvas_w=canvas_w, canvas_h=canvas_h)

    # Main meds card
    card_w = min(480, canvas_w * 0.38)
    card_h = 220
    card_x = 280 if canvas_w >= 600 else 20
    card_y = 110
    rounded_rect(t, card_x, card_y, card_w, card_h, r=16,
                 stroke=PALETTE["card_border"], fill=PALETTE["card_bg"], stroke_width=2.0,
                 canvas_w=canvas_w, canvas_h=canvas_h)

    # "Taken" chip inside card
    pill_chip(t, card_x + 28, card_y + 90, 84, 28,
              color_bg=PALETTE["success_bg"], color_border=PALETTE["success_bg"],
              label_width=60, canvas_w=canvas_w, canvas_h=canvas_h)

    # 'Mark as Not Taken' button (grey-ish)
    rounded_rect(t, card_x + 20, card_y + card_h - 56, card_w - 40, 36, r=8,
                 stroke=PALETTE["divider"], fill=PALETTE["divider"], stroke_width=1.0,
                 canvas_w=canvas_w, canvas_h=canvas_h)

    # Summary chips below card
    chip_w = 200
    chip_h = 70
    spacing = 24
    base_y = card_y + card_h + 32
    rounded_rect(t, card_x, base_y, chip_w, chip_h, r=12,
                 stroke=PALETTE["divider"], fill=PALETTE["card_bg"], stroke_width=1.0,
                 canvas_w=canvas_w, canvas_h=canvas_h)
    rounded_rect(t, card_x + chip_w + spacing, base_y, chip_w, chip_h, r=12,
                 stroke=PALETTE["divider"], fill=PALETTE["card_bg"], stroke_width=1.0,
                 canvas_w=canvas_w, canvas_h=canvas_h)

    # Return SVG text
    # SvgTurtle supports getting the SVG string (without saving to disk).
    svg_text = t.to_svg()  # method available per project discussions/issues
    return svg_text

def draw_score_svg(canvas_w: int, canvas_h: int) -> str:
    """
    Draws adherence gauge: grey ring + orange arc and a small card stack.
    """
    t = SvgTurtle(canvas_w, canvas_h)

    # Background
    rounded_rect(t, 0, 0, canvas_w, canvas_h, r=0,
                 stroke=PALETTE["page_bg"], fill=PALETTE["page_bg"], stroke_width=0.0,
                 canvas_w=canvas_w, canvas_h=canvas_h)

    # Gauge container card
    gauge_card_w = 340
    gauge_card_h = 300
    gauge_card_x = (canvas_w - gauge_card_w) / 2
    gauge_card_y = 90
    rounded_rect(t, gauge_card_x, gauge_card_y, gauge_card_w, gauge_card_h, r=22,
                 stroke=PALETTE["divider"], fill=PALETTE["card_bg"], stroke_width=1.5,
                 canvas_w=canvas_w, canvas_h=canvas_h)

    # Gauge ring
    cx = gauge_card_x + gauge_card_w/2
    cy = gauge_card_y + gauge_card_h/2 - 10
    radius = 100
    thickness = 18
    # Full ring (grey)
    circle_ring(t, cx, cy, radius, thickness, PALETTE["gauge_ring"], canvas_w, canvas_h, start_heading=0, extent=360)
    # Orange arc (e.g., 14% adherence → ~50° arc)
    adherence_pct = 14
    arc_deg = 360 * adherence_pct / 100.0
    circle_ring(t, cx, cy, radius, thickness, PALETTE["gauge_orange"], canvas_w, canvas_h,
                start_heading=90, extent=arc_deg)  # start at top

    # Small stat cards
    base_y = gauge_card_y + gauge_card_h + 28
    card_w = 380
    card_h = 74
    rounded_rect(t, (canvas_w - card_w)/2, base_y, card_w, card_h, r=12,
                 stroke=PALETTE["divider"], fill=PALETTE["card_bg"], stroke_width=1.0,
                 canvas_w=canvas_w, canvas_h=canvas_h)
    rounded_rect(t, (canvas_w - card_w)/2, base_y + card_h + 16, card_w, card_h, r=12,
                 stroke=PALETTE["success_bg"], fill="#F2FBF6", stroke_width=1.0,
                 canvas_w=canvas_w, canvas_h=canvas_h)
    rounded_rect(t, (canvas_w - card_w)/2, base_y + 2*(card_h + 16), card_w, card_h, r=12,
                 stroke=PALETTE["divider"], fill=PALETTE["card_bg"], stroke_width=1.0,
                 canvas_w=canvas_w, canvas_h=canvas_h)

    svg_text = t.to_svg()
    return svg_text

# ---------- RENDER ----------
if screen == "Home":
    svg = draw_home_svg(W, H)
    show_svg(svg, W, H)
    st.caption("Shapes drawn with turtle commands written to SVG (svg_turtle), then embedded in Streamlit.")
elif screen == "Score":
    svg = draw_score_svg(W, H)
    show_svg(svg, W, H)
    st.caption("Circular gauge drawn with turtle arc + rings; adjust adherence_pct for dynamic arc extent.")
