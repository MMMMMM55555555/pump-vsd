import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

# ==========================================
# STREAMLIT UI SETUP & INTERACTIVE CONTROLS
# ==========================================
st.set_page_config(page_title="Klong Prem VSD & Parallel Performance", layout="wide")
st.title("BMA/Klong Prem Tunnel Drainage (Model: 2600VLZGM, 15CMS)")
st.markdown("**VSD PERFORMANCE, PARALLEL PUMP OPERATION & SYSTEM CURVES**")

# Input columns at the top of the page
col_pumps, col_Q, col_H = st.columns([1, 1.5, 1.5])
with col_pumps:
    num_pumps = st.radio('⚙️ Operating Pumps:', options=[1, 2, 3, 4], index=0, horizontal=True)
with col_Q:
    target_Q = st.slider('🎯 Target Capacity (Q) [m³/sec]:', min_value=0.0, max_value=120.0, value=60.0, step=1.0)
with col_H:
    target_H = st.slider('📏 Target Head (H) [m]:', min_value=0.0, max_value=25.0, value=15.0, step=0.5)

# ==========================================
# 1. STATION CONFIGURATION & BASE DATA
# ==========================================
Q_min_allowable = 7.5  # MCSF for a single pump

# Single Pump H-Q Curve Approximation
Q_100_raw = np.array([0, 7.5, 10, 15, 20, 24])
H_100_raw = np.array([21.20, 20.5, 19.8, 18.0, 14.5, 8.5])
p_H = np.poly1d(np.polyfit(Q_100_raw, H_100_raw, 3)) 

Q_100_safe = np.linspace(Q_min_allowable, 24, 100)
H_100_safe = p_H(Q_100_safe)

# Single Pump Efficiency Curve 
Q_eff_raw = np.array([5, 10, 15, 18, 20, 24])
Eff_100_raw = np.array([55, 72, 85, 87, 82, 55])
p_Eff = np.poly1d(np.polyfit(Q_eff_raw, Eff_100_raw, 3))
Q_eff = np.linspace(5, 24, 100)
Eff_100 = p_Eff(Q_eff)

# Single Pump NPSHreq 
Q_npsh_raw = np.array([0, 10, 15, 20, 24])
H_npsh_raw = np.array([4.0, 2.5, 4.2, 8.5, 16.0])
p_npsh = np.poly1d(np.polyfit(Q_npsh_raw, H_npsh_raw, 3))
Q_npsh = np.linspace(0, 24, 100)
H_npsh = p_npsh(Q_npsh)

# THE 4 SYSTEM RESISTANCE CURVES 
system_curves = {
    'Circulation (Chaopaya -1.5m to Weir +4.5m)': (6.0, 0.003333, 'royalblue', '-'),
    'Drainage DWL (Bang Bua -1.0m to Chaopaya +2.2m)': (3.20, 0.003333, 'black', '-'),
    'Drainage HWL (Bang Bua 0.0m to Chaopaya +2.2m)': (2.20, 0.003333, 'firebrick', '-'),
    'Drainage LWL (Bang Bua -2.0m to Weir 0.0m)': (2.00, 0.006666, 'seagreen', '-')
}
Q_sys = np.linspace(0, 120, 200)

# ==========================================
# 2. PLOT SETUP & FIGURE INITIALIZATION
# ==========================================
fig, ax1 = plt.subplots(figsize=(15, 9))

# Force backgrounds to solid white to prevent Streamlit Dark Mode issues
fig.patch.set_facecolor('white')
ax1.set_facecolor('white')

ax2 = ax1.twinx()
# Explicitly force the Efficiency labels to stay on the right side
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position("right")

bbox_style = dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="gray", linewidth=0.5, alpha=0.9)
halo = [pe.withStroke(linewidth=3, foreground='white')]

max_x = max(35, 25 * num_pumps + 10)

# ==========================================
# 3. PLOT SYSTEM CURVES & NPSH
# ==========================================
for name, (H_stat, k, color, ls) in system_curves.items():
    H_sys = H_stat + k * (Q_sys**2)
    ax1.plot(Q_sys, H_sys, color=color, linewidth=2, linestyle=ls, label=name)

ax1.plot(Q_npsh * num_pumps, H_npsh, color='darkorange', linewidth=2.5, linestyle=':', label="Pump NPSHreq (Station Total)")

npsh_head = 26.97
ax1.axhline(y=npsh_head, color='indianred', linestyle='--', linewidth=1.5, alpha=0.8)
npsh_text = ("NPSHav @ Bang Bua HWL +0.00 m\n"
             "(Sta sump W.L. = -1.57 m MSL)\n"
             "= 26.97 m. (approx.)\n"
             "Pump impeller level = -18.64 m MSL")
ax1.text(max_x - 2, npsh_head, npsh_text, color='maroon', fontsize=9, fontweight='bold', va='center', ha='right', bbox=bbox_style)

# --- PLOT INTERACTIVE TARGET LINES ---
ax1.axhline(y=target_H, color='gray', linestyle='--', linewidth=1.5, alpha=0.6)
ax1.text(1.5, target_H + 0.5, f'Target H: {target_H:.1f} m', color='dimgray', fontsize=11, fontweight='bold', ha='left')

ax1.axvline(x=target_Q, color='gray', linestyle='--', linewidth=1.5, alpha=0.6)
ax1.text(target_Q + 0.5, 48, f'Target Q: {target_Q:.1f} CMS', color='dimgray', fontsize=11, fontweight='bold')

# ==========================================
# 4. PLOT VSD CURVES (SCALED FOR PARALLEL OPERATION)
# ==========================================
speeds = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
colors = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#800080', '#56B4E9'] 

for i, speed_ratio in enumerate(speeds):
    Q_single_vsd = Q_100_safe * speed_ratio
    H_safe = H_100_safe * (speed_ratio**2)
    Q_parallel = Q_single_vsd * num_pumps
    ax1.plot(Q_parallel, H_safe, linewidth=2.5, color=colors[i], label='_nolegend_')
    
    true_max_head = 21.20 * (speed_ratio**2)
    Q_start = Q_parallel[0]
    H_start = H_safe[0]
    ax1.plot(Q_start, H_start, marker='o', color=colors[i], markersize=6)
    
    # Text shifted left to avoid axis crossover
    label_text = f"{int(speed_ratio * 100)}%\nMax: {true_max_head:.2f} m"
    ax1.text(Q_start + (0.6 * num_pumps), H_start, label_text, color=colors[i], fontsize=10, 
             fontweight='bold', ha='left', va='center', path_effects=halo)
    
    # --- FIND INTERSECTIONS ---
    if min(H_safe) <= target_H <= max(H_safe):
        Q_at_target_H = np.interp(target_H, H_safe[::-1], Q_parallel[::-1])
        ax1.plot(Q_at_target_H, target_H, marker='D', color=colors[i], markersize=6)
        ax1.text(Q_at_target_H + (0.5 * num_pumps), target_H - 1.2, f"{Q_at_target_H:.1f} CMS", color=colors[i], fontsize=9, fontweight='bold', path_effects=halo)

    if min(Q_parallel) <= target_Q <= max(Q_parallel):
        H_at_target_Q = np.interp(target_Q, Q_parallel, H_safe)
        ax1.plot(target_Q, H_at_target_Q, marker='s', color=colors[i], markersize=6)
        ax1.text(target_Q + (0.5 * num_pumps), H_at_target_Q + 0.5, f"{H_at_target_Q:.1f}m", color=colors[i], fontsize=9, fontweight='bold', path_effects=halo)

# ==========================================
# 5. PLOT EFFICIENCY & FORMAT CHART
# ==========================================
ax2.plot(Q_eff * num_pumps, Eff_100, color='crimson', linewidth=2.5, linestyle='-.', label="Pump Efficiency (100%)")

ax1.set_xlabel('TOTAL STATION CAPACITY ($m^3/sec$)', fontsize=12, fontweight='bold')
ax1.set_ylabel('HEAD (m)', fontsize=12, fontweight='bold')
ax2.set_ylabel('EFFICIENCY (%)', fontsize=12, fontweight='bold')

ax1.set_xlim(0, max_x)
ax1.set_ylim(0, 50)
ax2.set_ylim(0, 100)

ax1.set_xticks(np.arange(0, max_x + 1, 10))
ax1.set_xticks(np.arange(0, max_x + 1, 2), minor=True)
ax1.set_yticks(np.arange(0, 51, 10))
ax1.set_yticks(np.arange(0, 51, 2), minor=True)
ax2.set_yticks(np.arange(0, 101, 10))

ax1.grid(which='major', color='gray', linestyle='-', linewidth=0.6, alpha=0.6)
ax1.grid(which='minor', color='gray', linestyle=':', linewidth=0.5, alpha=0.4)

lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right', fontsize=9, facecolor='white', edgecolor='black', framealpha=0.95)

plt.tight_layout()

# Render the plot in the Streamlit app
st.pyplot(fig)