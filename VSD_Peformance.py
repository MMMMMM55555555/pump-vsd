import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Pump VSD Performance", layout="wide")
st.title("BMA/Nongbon Tunnel Drainage: VSD Performance")
st.markdown("**Model : 1800VLZGM, 10CMS. x 23m. x 284 min⁻¹ x 3000kW.**")

# Streamlit Slider (replaces Matplotlib slider)
current_H = st.slider('🎯 Adjust Target Head (m):', min_value=0.0, max_value=35.0, value=16.5, step=0.10)

# ==========================================
# 1. DATA EXTRACTION & APPROXIMATION
# ==========================================
Q_100_raw = np.array([7.2, 8.5, 10, 12, 14, 15.9, 16.5])
H_100_raw = np.array([27.5, 25.5, 23.0, 18.8, 13.5, 7.0, 4.0])
p_H = np.poly1d(np.polyfit(Q_100_raw, H_100_raw, 2))
Q_100 = np.linspace(7.2, 16.5, 100)
H_100 = p_H(Q_100)

Q_eff_raw = np.array([7.2, 9.0, 10.0, 11.5, 13.0, 14.5, 15.9, 16.8])
Eff_100_raw = np.array([35, 70, 83, 88, 85, 72, 45, 0])
p_Eff = np.poly1d(np.polyfit(Q_eff_raw, Eff_100_raw, 4))
Q_eff = np.linspace(7.2, 16.8, 100)
Eff_100 = p_Eff(Q_eff)

Q_npsh_raw = np.array([7.2, 10.0, 11.5, 13.0, 14.5, 15.9, 16.5])
H_npsh_raw = np.array([5.5, 2.0, 1.5, 2.2, 4.0, 7.0, 11.0])
p_npsh = np.poly1d(np.polyfit(Q_npsh_raw, H_npsh_raw, 3))
Q_npsh = np.linspace(7.2, 16.5, 100)
H_npsh = p_npsh(Q_npsh)

H_static = 5.5
k_sys = (7.0 - H_static) / (15.9**2)
Q_sys = np.linspace(0, 25, 100)
H_sys = H_static + k_sys * (Q_sys**2)

# ==========================================
# 2. PLOT SETUP 
# ==========================================
fig, ax1 = plt.subplots(figsize=(12, 8)) 
ax2 = ax1.twinx()

halo = [pe.withStroke(linewidth=3, foreground='white')]
bbox_style = dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#cccccc", linewidth=1, alpha=0.95)

# ==========================================
# 3. PLOT ANNOTATIONS & SYSTEM CURVES
# ==========================================
ax1.plot(Q_sys, H_sys, color='#556B2F', linewidth=2.5, label="System Resistance")
ax1.plot(Q_npsh, H_npsh, color='goldenrod', linewidth=2.5, label="Pump NPSHrq")

ax1.axhline(y=28.8, color='indianred', linestyle='--', linewidth=1.5, alpha=0.8)
ax1.text(25, 28.8, 'NPSHav @ HWL+0.00 m\n= 28.8m.(approx.)', color='maroon', fontsize=9, fontweight='bold', va='center', bbox=bbox_style)

ax1.axhline(y=10.55, color='indianred', linestyle='--', linewidth=1.5, alpha=0.8)
ax1.text(25, 10.55, 'NPSHav @ LWL-18.25 m\n= 10.55 m.(approx.)', color='maroon', fontsize=9, fontweight='bold', va='center', bbox=bbox_style)

ax1.vlines(x=10, ymin=0, ymax=45, color='rebeccapurple', linestyle='--', linewidth=1.5, alpha=0.7)
ax1.vlines(x=15.9, ymin=0, ymax=30, color='rebeccapurple', linestyle='--', linewidth=1.5, alpha=0.7)

# ==========================================
# 4. PLOT PUMP VSD CURVES & TARGET CALCULATION
# ==========================================
speeds = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
colors = ['#005B96', '#D68910', '#117A65', '#AF7AC5', '#884EA0', '#5DADE2'] 

ax1.axhline(y=current_H, color='red', linestyle='--', linewidth=1.5, alpha=0.6)
ax1.text(0.5, current_H + 0.5, f'Target Head = {current_H:.2f} m', color='red', fontsize=10, fontweight='bold')

for i, speed_ratio in enumerate(speeds):
    Q_new = Q_100 * speed_ratio
    H_new = H_100 * (speed_ratio**2)
    
    ax1.plot(Q_new, H_new, linewidth=2.5, color=colors[i], label='_nolegend_')
    ax1.text(Q_new[0] - 0.4, H_new[0] + 0.2, f"{int(speed_ratio * 100)}%", 
             color=colors[i], fontsize=12, fontweight='900', ha='right', va='bottom', path_effects=halo)

    if np.max(H_new) >= current_H >= np.min(H_new):
        target_Q = np.interp(current_H, H_new[::-1], Q_new[::-1])
        ax1.plot(target_Q, current_H, marker='o', color='red', markersize=6)
        ax1.annotate(f'Q = {target_Q:.2f}\n({int(speed_ratio * 100)}%)', 
                     xy=(target_Q, current_H), xytext=(target_Q - 0.5, current_H + 2 + (i*1.5)), 
                     arrowprops=dict(facecolor='red', edgecolor='red', arrowstyle='-', lw=1), 
                     fontsize=9, fontweight='bold', color='red', 
                     bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffe6e6", edgecolor="red", alpha=0.9))

ax2.plot(Q_eff, Eff_100, color='#C0392B', linewidth=2.5, linestyle='-.', label="Pump Efficiency (100%)")

# ==========================================
# 5. CHART FORMATTING & TITLES
# ==========================================
ax1.set_xlabel('CAPACITY ($m^3/sec$)', fontsize=12, fontweight='bold', labelpad=10)
ax1.set_ylabel('HEAD (m)', fontsize=12, fontweight='bold', labelpad=10)
ax2.set_ylabel('EFFICIENCY (%)', fontsize=12, fontweight='bold', labelpad=10)

ax1.set_xlim(0, 40)
ax1.set_ylim(0, 50)
ax2.set_ylim(0, 100)

ax1.set_xticks(np.arange(0, 41, 10))
ax1.set_xticks(np.arange(0, 41, 2), minor=True)
ax1.set_yticks(np.arange(0, 51, 10))
ax1.set_yticks(np.arange(0, 51, 2), minor=True)
ax2.set_yticks(np.arange(0, 101, 10))

ax1.grid(which='major', color='#999999', linestyle='-', linewidth=0.6, alpha=0.6)
ax1.grid(which='minor', color='#cccccc', linestyle=':', linewidth=0.6, alpha=0.5)

lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right', 
           fontsize=10, facecolor='#f9f9f9', edgecolor='#999999', framealpha=0.95, borderpad=0.8)

plt.tight_layout()

# Render the plot in Streamlit
st.pyplot(fig)