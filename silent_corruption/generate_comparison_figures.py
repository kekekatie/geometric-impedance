#!/usr/bin/env python3
"""
Generate comparison figures for Silent Relational Corruption paper v3.
Apples-to-apples AB vs Penrose at matched scale.
"""

import matplotlib.pyplot as plt
import numpy as np

# Data from matched-scale audits (interior-75% subsets)
data = {
    'AB': {
        'N': 16997,
        'native_core': 752,
        'identity_address': 0.986,
        'identity_weave': 0.991,
        'identity_hybrid': 0.989,
        'fresh_address': 0.542,
        'fresh_weave': 0.892,
        'fresh_hybrid': 0.890,
    },
    'Penrose': {
        'N': 21539,
        'native_core': 208,
        'identity_address': 0.661,
        'identity_weave': 0.830,
        'identity_hybrid': 0.855,
        'fresh_address': 0.524,
        'fresh_weave': 0.912,
        'fresh_hybrid': 0.914,
    }
}

# Figure 1: 2x2 panel - Identity vs Fresh for both substrates
fig, axes = plt.subplots(2, 2, figsize=(10, 8))

feature_sets = ['address', 'weave', 'hybrid']
colors = {'address': '#2166ac', 'weave': '#b2182b', 'hybrid': '#4dac26'}
labels = {'address': 'Address', 'weave': 'Weave', 'hybrid': 'Hybrid'}

for row, substrate in enumerate(['AB', 'Penrose']):
    for col, audit in enumerate(['identity', 'fresh']):
        ax = axes[row, col]

        values = [data[substrate][f'{audit}_{fs}'] for fs in feature_sets]
        x = np.arange(len(feature_sets))
        bars = ax.bar(x, values, color=[colors[fs] for fs in feature_sets], edgecolor='black', linewidth=0.5)

        ax.set_ylim(0.4, 1.05)
        ax.axhline(0.5, color='gray', linestyle='--', linewidth=0.8, alpha=0.7, label='Chance' if row==0 and col==0 else '')
        ax.set_xticks(x)
        ax.set_xticklabels([labels[fs] for fs in feature_sets])
        ax.set_ylabel('AUC')

        title = f"{substrate}: {'Identity Persistence' if audit == 'identity' else 'Fresh Reconstruction'}"
        ax.set_title(title, fontsize=11, fontweight='bold')

        # Add value labels on bars
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                   f'{val:.3f}', ha='center', va='bottom', fontsize=9)

        ax.grid(axis='y', alpha=0.3)

fig.suptitle('Silent Relational Corruption: Matched-Scale Validation\n(5E rewiring, 10 replicates, interior-75% subsets)',
             fontsize=12, fontweight='bold')
plt.tight_layout()
fig.savefig('C:/Users/Karen/Downloads/figure1_identity_vs_fresh_2x2.png', dpi=200, bbox_inches='tight')
plt.close(fig)
print("Saved: figure1_identity_vs_fresh_2x2.png")


# Figure 2: Direct AB vs Penrose comparison for identity audit
fig, ax = plt.subplots(figsize=(8, 5))

x = np.arange(3)
width = 0.35

ab_vals = [data['AB']['identity_address'], data['AB']['identity_weave'], data['AB']['identity_hybrid']]
pen_vals = [data['Penrose']['identity_address'], data['Penrose']['identity_weave'], data['Penrose']['identity_hybrid']]

bars1 = ax.bar(x - width/2, ab_vals, width, label=f"AB (N={data['AB']['N']:,})", color='#2166ac', edgecolor='black')
bars2 = ax.bar(x + width/2, pen_vals, width, label=f"Penrose (N={data['Penrose']['N']:,})", color='#b2182b', edgecolor='black')

ax.set_ylim(0.5, 1.05)
ax.axhline(0.5, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)
ax.set_xticks(x)
ax.set_xticklabels(['Address', 'Weave', 'Hybrid'])
ax.set_ylabel('Identity Persistence AUC', fontsize=11)
ax.set_xlabel('Feature Set', fontsize=11)
ax.set_title('Exo/Endo Split: Identity Persistence Under 5E Relational Scrambling', fontsize=12, fontweight='bold')
ax.legend(loc='lower right')
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.015, f'{height:.3f}',
               ha='center', va='bottom', fontsize=9)

plt.tight_layout()
fig.savefig('C:/Users/Karen/Downloads/figure2_ab_vs_penrose_identity.png', dpi=200, bbox_inches='tight')
plt.close(fig)
print("Saved: figure2_ab_vs_penrose_identity.png")


# Figure 3: Summary comparison table as figure
fig, ax = plt.subplots(figsize=(10, 4))
ax.axis('off')

table_data = [
    ['Metric', 'AB (interior-75%)', 'Penrose (interior-75%)', 'Interpretation'],
    ['Nodes', f"{data['AB']['N']:,}", f"{data['Penrose']['N']:,}", 'Matched scale'],
    ['Native core', str(data['AB']['native_core']), str(data['Penrose']['native_core']), 'Both adequate for CV'],
    ['Identity Address AUC', f"{data['AB']['identity_address']:.3f}", f"{data['Penrose']['identity_address']:.3f}", 'AB near-ceiling, Penrose weak'],
    ['Identity Hybrid AUC', f"{data['AB']['identity_hybrid']:.3f}", f"{data['Penrose']['identity_hybrid']:.3f}", 'Penrose needs hybrid'],
    ['Fresh Weave AUC', f"{data['AB']['fresh_weave']:.3f}", f"{data['Penrose']['fresh_weave']:.3f}", 'Both weave-led'],
]

table = ax.table(cellText=table_data, loc='center', cellLoc='center',
                colWidths=[0.22, 0.18, 0.20, 0.30])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.8)

# Style header row
for j in range(4):
    table[(0, j)].set_facecolor('#4a4a4a')
    table[(0, j)].set_text_props(color='white', fontweight='bold')

# Alternate row colors
for i in range(1, len(table_data)):
    color = '#f0f0f0' if i % 2 == 0 else 'white'
    for j in range(4):
        table[(i, j)].set_facecolor(color)

ax.set_title('Matched-Scale Comparison: Silent Relational Corruption Audit',
             fontsize=12, fontweight='bold', pad=20)
plt.tight_layout()
fig.savefig('C:/Users/Karen/Downloads/figure3_comparison_table.png', dpi=200, bbox_inches='tight')
plt.close(fig)
print("Saved: figure3_comparison_table.png")

print("\nAll figures generated successfully!")
