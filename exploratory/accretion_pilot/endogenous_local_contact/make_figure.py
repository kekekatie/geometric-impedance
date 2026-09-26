#!/usr/bin/env python3
"""Small event diagram: the two LOCAL event types (BUD, CONTACT) that compete in one
scheduler (uniform over their union) -- no global sweep, no external clock. Same active
front, different archive => different CONTACT menu => different next-active distribution."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
A, Q, NEW = "#d62728", "#c9c9c9", "#1a7f37"


def node(ax, xy, lab, active=True, s=460):
    ax.scatter([xy[0]], [xy[1]], s=s, c=(A if active else Q), edgecolors="k",
               zorder=3, linewidths=1.1)
    ax.text(xy[0], xy[1], lab, ha="center", va="center",
            color=("white" if active else "#333"), fontsize=11, fontweight="bold", zorder=4)


fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))

# ---- panel A: the two local event types ----
ax = axes[0]
# BUD
node(ax, (0, 2.1), "1"); node(ax, (1, 2.1), "1")
ax.plot([0, 1], [2.1, 2.1], "-", color=A, lw=2.8)
ax.annotate("", xy=(2.3, 2.1), xytext=(1.4, 2.1), arrowprops=dict(arrowstyle="-|>", lw=1.8, color="#444"))
ax.text(1.85, 2.32, "BUD", fontsize=8.5, ha="center", color="#444")
node(ax, (2.7, 2.1), "1"); node(ax, (3.7, 1.7), "0"); node(ax, (3.7, 2.5), "1")
ax.plot([2.7, 3.7], [2.1, 2.5], "-", color=A, lw=2.8)
ax.plot([2.7, 3.7], [2.1, 1.7], "-", color="#bbb", lw=1.4)
ax.plot([3.7, 3.7], [1.7, 2.5], "-", color="#bbb", lw=1.4)
ax.text(-0.15, 2.1, "BUD:", fontsize=9, ha="right", va="center", fontweight="bold")

# CONTACT
node(ax, (0, 0.4), "1"); node(ax, (1, 0.4), "0"); node(ax, (2, 0.4), "1")
ax.plot([0, 1], [0.4, 0.4], "--", color="#999", lw=1.5)
ax.plot([1, 2], [0.4, 0.4], "--", color="#999", lw=1.5)
ax.annotate("", xy=(3.3, 0.4), xytext=(2.4, 0.4), arrowprops=dict(arrowstyle="-|>", lw=1.8, color="#444"))
ax.text(2.85, 0.62, "CONTACT", fontsize=8.5, ha="center", color="#444")
node(ax, (3.7, 0.8), "1"); node(ax, (5.0, 0.8), "1"); node(ax, (4.35, 0.0), "0")
ax.plot([3.7, 5.0], [0.8, 0.8], "-", color=NEW, lw=3.0)
ax.plot([3.7, 4.35], [0.8, 0.0], "--", color="#999", lw=1.4)
ax.plot([5.0, 4.35], [0.8, 0.0], "--", color="#999", lw=1.4)
ax.text(-0.15, 0.4, "CONTACT:", fontsize=9, ha="right", va="center", fontweight="bold")
ax.text(2.5, -0.75, "one step = pick uniformly from  {all BUD events} ∪ {all CONTACT events}\n"
                    "every event is LOCAL — no global sweep, no external clock (autonomous)",
        ha="center", fontsize=8.5, color="#111",
        bbox=dict(boxstyle="round", fc="#eef6ff", ec="#5b8bd0"))
ax.set_xlim(-1.4, 5.4); ax.set_ylim(-1.3, 2.9); ax.axis("off")
ax.set_title("two local event types (extended rule set — a modelling assumption)", fontsize=10)

# ---- panel B: same front, different archive -> different menu -> different distribution ----
ax = axes[1]
ax.axis("off")
ax.set_title("same active front, different archive → different event menu", fontsize=10)
txt = (
    "state 0   archive 0-degrees {3,3}\n"
    "   event menu:  4 BUD  ⊕  1 CONTACT   (total 5)\n"
    "   1-event active-successor dist:  {c0: 4/5,  c1: 1/5}\n"
    "   2-event:  {c0: 59/75, c1: 11/75, c2: 1/15}\n"
    "\n"
    "state 1   archive 0-degrees {2,3}\n"
    "   event menu:  4 BUD  ⊕  2 CONTACT   (total 6)\n"
    "   1-event active-successor dist:  {c0: 2/3,  c1: 1/3}\n"
    "   2-event:  {c0: 403/630, c1: 137/630, c2: 2/21, c3: 1/21}\n"
    "\n"
    "BUD-only (coupling off):  both states  {c0: 1}  — identical\n"
    "→ the archive matters ONLY via the CONTACT coupling"
)
ax.text(0.02, 0.98, txt, ha="left", va="top", fontsize=9.5, family="monospace",
        transform=ax.transAxes)
ax.text(0.02, 0.06, "distinct quiet mediators = distinct CONTACT events (even for the same edge)",
        ha="left", va="top", fontsize=8, color="#555", transform=ax.transAxes)

fig.suptitle("Autonomous asynchronous CONTACT: a local event, not a global sweep — and the "
             "archive's relations change the active future.", fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig(os.path.join(HERE, "figures", "local_contact_event.png"), dpi=140)
print("wrote figures/local_contact_event.png")
