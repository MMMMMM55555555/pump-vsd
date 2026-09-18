import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

# ==========================================
# STREAMLIT UI SETUP & INTERACTIVE SLIDERS
# ==========================================
st.set_page_config(page_title="Klong Prem VSD Performance", layout="wide")
st.title("BMA/Klong Prem Tunnel Drainage (Model: 2600VLZGM, 15CMS)")
st.markdown("**VSD PERFORMANCE & OPERATING TARGETS**")

# Place sliders side-by-side at the top of the app
col1, col2 = st.columns(2)
with col1:
    target_Q = st.slider('🎯 Target Capacity (Q) [m³/sec]:', min_value=0.0, max_value=30.0, value=15.0, step=0.5)
with col2:
    target_H = st.slider('📏 Target Head (H) [m]:', min_value=0.0, max_value=25.0, value=12.0, step=0.5)

# ==========================================
# 1. STATION CONFIGURATION & BASE DATA
# ==========================================
Q_min_allowable = 8.0  # MCSF: Start of the solid curve

# H-Q Curve Approximation (3rd-Degree Polynomial to prevent artificial parabolic humps)
Q_100_raw = np.array([0, 5, 10, 15, 20, 24])
H_100_raw = np.array([20.5, 20.3, 19.5, 18.0, 14.5, 6.0])
p_H = np.poly1d(np.polyfit(Q_100_raw, H_100_raw, 3)) 

Q_100_safe = np.linspace(Q_min_allowable, 24, 100)
H_100_safe = p_H(Q_100_safe)

# Efficiency Curve 
Q_eff_raw = np.array([5, 10, 15, 18, 20, 24])
Eff_100_raw = np.array([55, 72, 85, 87, 82, 55])
p_Eff = np.poly1d(np.polyfit(Q_eff_raw, Eff_100_raw, 3))
Q_eff = np.linspace(5, 24, 100)
Eff_100 = p_Eff(Q_eff)

# Pump NPSHrq (Hockey Stick Interpolation)
Q_npsh = np.linspace(8, 22.5, 100)
Q_npsh_raw = np.array([8, 10, 13, 16, 18, 19, 20, 21, 21.5, 22, 22.5])
H_npsh_raw = np.array([7.2, 6.2, 5.5, 5.5, 6.0, 6.8, 8.5, 13.0, 18.0, 28.0, 45.0])
H_npsh = np.interp(Q_npsh, Q_npsh_raw, H_npsh_raw)

# System Resistance Curve
H_static = 6.0
k_sys = (15.0 - H_static) / (60**2) 
Q_sys = np.linspace(0, 35, 100)
H_sys = H_static + k_sys * (Q_sys**2)

# ==========================================
# 2. PLOT SETUP 
# ==========================================
fig, ax1 = plt.subplots(figsize=(15, 9))

# FIX FOR STREAMLIT BLACK SCREEN ISSUE: Force figure and axes backgrounds to solid white
fig.patch.set_facecolor('white')
ax1.set_facecolor('white')

ax2 = ax1.twinx()

bbox_style = dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="gray", linewidth=0.5, alpha=0.9)
halo = [pe.withStroke(linewidth=3, foreground='white')]

# --- PLOT SYSTEM CURVES ---
ax1.plot(Q_sys, H_sys, color='#556B2F', linewidth=2, label="System Resistance")
ax1.plot(Q_npsh, H_npsh, color='goldenrod', linewidth=2.5, label="Pump NPSHrq")

# Static NPSHav Line & Text Block
npsh_head = 26.97
ax1.axhline(y=npsh_head, color='indianred', linestyle='--', linewidth=1.5, alpha=0.8)
npsh_text = ("NPSHav @ Bang Bua HWL +0.00 m\n"
             "(Sta sump W.L. = -1.57 m MSL)\n"
             "= 26.97 m. (approx.)\n"
             "Pump impeller level = -18.64 m MSL")
ax1.text(22, npsh_head, npsh_text, color='maroon', fontsize=10, fontweight='bold', va='center', bbox=bbox_style)

# --- PLOT INTERACTIVE TARGET LINES ---
ax1.axhline(y=target_H, color='gray', linestyle='--', linewidth=1.5, alpha=0.6)
ax1.text(34.5, target_H + 0.5, f'Target H: {target_H:.1f} m', color='dimgray', fontsize=11, fontweight='bold', ha='right')

ax1.axvline(x=target_Q, color='gray', linestyle='--', linewidth=1.5, alpha=0.6)
ax1.text(target_Q + 0.3, 48, f'Target Q: {target_Q:.1f} CMS', color='dimgray', fontsize=11, fontweight='bold')

# --- PLOT VSD CURVES ---
speeds = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
colors = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#800080', '#56B4E9'] 

for i, speed_ratio in enumerate(speeds):
    Q_safe = Q_100_safe * speed_ratio
    H_safe = H_100_safe * (speed_ratio**2)
    
    # Plot the main solid curve
    ax1.plot(Q_safe, H_safe, linewidth=2.5, color=colors[i], label='_nolegend_')
    
    # Find the TRUE absolute max head across the entire theoretical array to ensure accuracy
    Q_theoretical = np.linspace(0, 24, 200) * speed_ratio
    H_theoretical = p_H(np.linspace(0, 24, 200)) * (speed_ratio**2)
    true_max_head = np.max(H_theoretical)
    
    # Anchor the label directly to the start of the solid curve (MCSF)
    Q_start = Q_safe[0]
    H_start = H_safe[0]
    ax1.plot(Q_start, H_start, marker='o', color=colors[i], markersize=6)
    
    label_text = f"{int(speed_ratio * 100)}%\nMax Head: {true_max_head:.2f} m"
    ax1.text(Q_start - 0.4, H_start, label_text, color=colors[i], fontsize=10, fontweight='bold', ha='right', va='center')
    
    # --- FIND INTERSECTIONS ---
    if min(H_safe) <= target_H <= max(H_safe):
        Q_at_target_H = np.interp(target_H, H_safe[::-1], Q_safe[::-1])
        ax1.plot(Q_at_target_H, target_H, marker='D', color=colors[i], markersize=6)
        ax1.text(Q_at_target_H + 0.3, target_H - 1.2, f"{Q_at_target_H:.1f} CMS", color=colors[i], fontsize=9, fontweight='bold', path_effects=halo)

    if min(Q_safe) <= target_Q <= max(Q_safe):
        H_at_target_Q = np.interp(target_Q, Q_safe, H_safe)
        ax1.plot(target_Q, H_at_target_Q, marker='s', color=colors[i], markersize=6)
        ax1.text(target_Q + 0.3, H_at_target_Q + 0.5, f"{H_at_target_Q:.1f}m", color=colors[i], fontsize=9, fontweight='bold', path_effects=halo)

# --- PLOT EFFICIENCY ---
ax2.plot(Q_eff, Eff_100, color='crimson', linewidth=2.5, linestyle='-.', label="Pump Efficiency (100%)")

# --- CHART FORMATTING ---
ax1.set_xlabel('CAPACITY ($m^3/sec$)', fontsize=12, fontweight='bold')
ax1.set_ylabel('HEAD (m)', fontsize=12, fontweight='bold')
ax2.set_ylabel('EFFICIENCY (%)', fontsize=12, fontweight='bold')

ax1.set_xlim(0, 35)
ax1.set_ylim(0, 50)
ax2.set_ylim(0, 100)

ax1.set_xticks(np.arange(0, 36, 5))
ax1.set_xticks(np.arange(0, 36, 1), minor=True)
ax1.set_yticks(np.arange(0, 51, 10))
ax1.set_yticks(np.arange(0, 51, 2), minor=True)
ax2.set_yticks(np.arange(0, 101, 10))

ax1.grid(which='major', color='gray', linestyle='-', linewidth=0.6, alpha=0.6)
ax1.grid(which='minor', color='gray', linestyle=':', linewidth=0.5, alpha=0.4)

lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right', fontsize=10, facecolor='white', edgecolor='black', framealpha=0.95)

plt.tight_layout()

# Render the plot in the Streamlit app
st.pyplot(fig)