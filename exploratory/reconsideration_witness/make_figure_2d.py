"""Generate onset_lip_2d.svg: the 2D onset-lip witness bracket, two panels.

Panel A (space): a rotated surface-code patch; a lost data qubit sits in a diamond
of four checks (2 X, 2 Z) -- its star -- which is the spatial bracket.
Panel B (spacetime): the loss opens a vertical tube from an ambiguous onset; the
bracket is that diamond at the earliest-onset LIP, below the commit cut.

Pure-Python SVG, no dependencies. Run: python3 make_figure_2d.py
"""

X_FILL = "#bcd0e6"   # X-plaquette (detects Z errors)
Z_FILL = "#f3d6b0"   # Z-plaquette (detects X errors)
X_EDGE = "#4e79a7"
Z_EDGE = "#c67b2e"
DATA = "#3a3a3a"
LOST = "#d1495b"
BR = "#2a9d8f"       # bracket highlight
PR = "#ececec"       # pruned slab
INK = "#222"


def panel_A(ox, oy, s=52):
    """Rotated d=5 patch, top-down. Data dots 5x5; interior plaquettes 4x4."""
    out = [f'<text x="{ox}" y="{oy-18}" '
           f'font-size="15" font-weight="bold" fill="{INK}">A &#183; space: the loss sits in a 4-check diamond</text>']
    # plaquettes (i,j) for i,j in 0..3, centre between data dots
    for i in range(4):
        for j in range(4):
            cx, cy = ox + (i + 0.5) * s, oy + (j + 0.5) * s
            isX = (i + j) % 2 == 0
            fill, edge = (X_FILL, X_EDGE) if isX else (Z_FILL, Z_EDGE)
            star = i in (1, 2) and j in (1, 2)           # the 4 around centre (2,2)
            sw = 3.2 if star else 1.0
            ec = BR if star else edge
            out.append(f'<rect x="{cx-s/2:.1f}" y="{cy-s/2:.1f}" width="{s}" height="{s}" '
                       f'fill="{fill}" stroke="{ec}" stroke-width="{sw}"/>')
            lab = "X" if isX else "Z"
            out.append(f'<text x="{cx:.1f}" y="{cy+5:.1f}" text-anchor="middle" '
                       f'font-size="13" fill="{edge}">{lab}</text>')
    # data qubits
    for i in range(5):
        for j in range(5):
            cx, cy = ox + i * s, oy + j * s
            if i == 2 and j == 2:
                out.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{LOST}"/>')
                out.append(f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="11" '
                           f'fill="white" font-weight="bold">&#215;</text>')
            else:
                out.append(f'<circle cx="{cx}" cy="{cy}" r="4.5" fill="{DATA}"/>')
    out.append(f'<text x="{ox}" y="{oy+4*s+28}" font-size="12.5" '
               f'fill="{INK}">lost qubit D (red) &#8594; its star = 2 X + 2 Z checks '
               f'(teal) = the spatial bracket</text>')
    return "\n".join(out)


def panel_B(ox, oy, w=250, rh=46):
    """Spacetime side view: one spatial slice (x) vs time (rounds, up)."""
    rounds = 6                     # 0..5, drawn bottom(0) to top(5)
    cut = 3                        # commit cut between round 2 and 3
    onsets = [1, 2]                # ambiguous onset floors
    lossx = ox + w * 0.5
    def ty(r):                     # time -> y (higher round = higher up)
        return oy + (rounds - 1 - r) * rh
    out = [f'<text x="{ox}" y="{oy-18}" font-size="15" '
           f'font-weight="bold" fill="{INK}">B &#183; spacetime: the diamond at the onset lip</text>']
    # pruned slab (rounds 0..cut-1)
    out.append(f'<rect x="{ox}" y="{ty(cut-1)-rh/2:.1f}" width="{w}" height="{cut*rh}" '
               f'fill="{PR}"/>')
    # round gridlines + labels
    for r in range(rounds):
        y = ty(r)
        out.append(f'<line x1="{ox}" y1="{y:.1f}" x2="{ox+w}" y2="{y:.1f}" '
                   f'stroke="#ccc" stroke-width="1"/>')
        out.append(f'<text x="{ox-8}" y="{y+4:.1f}" text-anchor="end" font-size="11" '
                   f'fill="#777">r{r}</text>')
    # commit cut
    ycut = (ty(cut) + ty(cut - 1)) / 2
    out.append(f'<line x1="{ox}" y1="{ycut:.1f}" x2="{ox+w}" y2="{ycut:.1f}" '
               f'stroke="{INK}" stroke-width="2" stroke-dasharray="7 4"/>')
    out.append(f'<text x="{ox+w+6}" y="{ycut+4:.1f}" font-size="11" fill="{INK}">commit cut</text>')
    out.append(f'<text x="{ox+w/2:.0f}" y="{ty(1)+rh/2+16:.1f}" text-anchor="middle" '
               f'font-size="11" fill="#999">pruned slab &#8594; frame + boundary only</text>')
    out.append(f'<text x="{ox+w/2:.0f}" y="{ty(cut)-rh/2-7:.1f}" text-anchor="middle" '
               f'font-size="11" fill="#999">thin live buffer</text>')
    # loss tube from earliest onset up
    out.append(f'<rect x="{lossx-11:.1f}" y="{ty(rounds-1)-rh/2:.1f}" width="22" '
               f'height="{(rounds-1-onsets[0]+1)*rh:.1f}" fill="{LOST}" opacity="0.16"/>')
    out.append(f'<line x1="{lossx:.1f}" y1="{ty(rounds-1)-rh/2:.1f}" x2="{lossx:.1f}" '
               f'y2="{ty(onsets[0]):.1f}" stroke="{LOST}" stroke-width="2" stroke-dasharray="3 3"/>')
    # the two candidate diamonds (bracket) at the onset floors
    for k, r in enumerate(onsets):
        y = ty(r)
        for dx in (-26, 26):       # the two side checks of the star in this slice
            out.append(f'<rect x="{lossx+dx-10:.1f}" y="{y-10:.1f}" width="20" height="20" '
                       f'fill="none" stroke="{BR}" stroke-width="3" transform="rotate(45 {lossx+dx:.1f} {y:.1f})"/>')
        out.append(f'<circle cx="{lossx:.1f}" cy="{y:.1f}" r="6" fill="{LOST}"/>')
        tag = "lip (earliest onset)" if k == 0 else "later candidate onset"
        out.append(f'<text x="{ox+w+6}" y="{y+4:.1f}" font-size="10.5" fill="{BR}">{tag}</text>')
    out.append(f'<text x="{ox}" y="{oy+rounds*rh+6:.0f}" '
               f'font-size="12.5" fill="{INK}">keep the diamond LIVE across the cut: '
               f'O(1) per loss, not O(d&#178;&#183;L)</text>')
    return "\n".join(out)


def build():
    W, H = 910, 420
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'font-family="Helvetica,Arial,sans-serif">',
           f'<rect width="{W}" height="{H}" fill="white"/>',
           f'<text x="{W/2}" y="26" text-anchor="middle" font-size="17" font-weight="bold" '
           f'fill="{INK}">The 2D onset-lip witness bracket around a lost qubit</text>',
           panel_A(55, 80),
           panel_B(500, 80),
           '</svg>']
    return "\n".join(svg)


if __name__ == '__main__':
    with open('onset_lip_2d.svg', 'w') as f:
        f.write(build())
    print("wrote onset_lip_2d.svg")
