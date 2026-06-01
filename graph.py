import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 1. Chargement des données CSV
cmd_vel = pd.read_csv('cmd_vel_full.csv')
odom = pd.read_csv('odom_full.csv')

# 2. Alignement temporel par rapport au premier point de l'odométrie (t0 = 0s)
t0 = odom['timestamp_ns'].min()
odom['time_rel'] = (odom['timestamp_ns'] - t0) / 1e9
cmd_vel['time_rel'] = (cmd_vel['timestamp_ns'] - t0) / 1e9

# 3. Création d'une grille uniforme à 100 Hz (pas de 10 ms)
time_grid = np.arange(0, max(odom['time_rel'].max(), cmd_vel['time_rel'].max()), 0.01)

# Interpolation des signaux
vel_x_interp = np.interp(time_grid, odom['time_rel'], odom['vel_x'])
vel_y_interp = np.interp(time_grid, odom['time_rel'], odom['vel_y'])
linear_x_interp = np.interp(time_grid, cmd_vel['time_rel'], cmd_vel['linear_x'], left=0.0, right=0.0)
linear_y_interp = np.interp(time_grid, cmd_vel['time_rel'], cmd_vel['linear_y'], left=0.0, right=0.0)

df_sync = pd.DataFrame({
    'time': time_grid,
    'consigne_x': linear_x_interp,
    'reel_x': vel_x_interp,
    'consigne_y': linear_y_interp,
    'reel_y': vel_y_interp
})

# Calcul des erreurs et des tendances lissées (fenêtre de 1 seconde = 100 échantillons)
df_sync['error_x_smooth'] = (df_sync['consigne_x'] - df_sync['reel_x']).rolling(100, center=True, min_periods=1).mean()
df_sync['error_y_smooth'] = (df_sync['consigne_y'] - df_sync['reel_y']).rolling(100, center=True, min_periods=1).mean()

# 4. Génération du graphique avec deux sous-graphiques distincts (Subplots)
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 8))

# --- AXE X : Comportement Longitudinal ---
ax1.plot(df_sync['time'], df_sync['consigne_x'], label='Consigne $V_x$', color='blue', linewidth=2)
ax1.plot(df_sync['time'], df_sync['reel_x'], label='Réel $V_x$ (Odom\'etrie)', color='orange', linewidth=1.2, alpha=0.8)
ax1.plot(df_sync['time'], df_sync['error_x_smooth'], label='Tendance Patinage X', color='darkblue', linewidth=2, linestyle='--')
ax1.set_ylabel('Vitesse / Erreur X ($m/s$)')
ax1.set_title('Analyse Cinématique Distincte : Suivi de Vitesse et Patinage (Axes X et Y)')
ax1.legend(loc='upper right', ncol=3)
ax1.grid(True, linestyle='--', alpha=0.5)

# --- AXE Y : Comportement Latéral ---
ax2.plot(df_sync['time'], df_sync['consigne_y'], label='Consigne $V_y$', color='green', linewidth=2)
ax2.plot(df_sync['time'], df_sync['reel_y'], label='R\'eel $V_y$ (Odom\'etrie)', color='red', linewidth=1.2, alpha=0.8)
ax2.plot(df_sync['time'], df_sync['error_y_smooth'], label='Tendance Patinage Y', color='crimson', linewidth=2, linestyle='--')
ax2.set_xlabel('Temps ($s$)')
ax2.set_ylabel('Vitesse / Erreur Y ($m/s$)')
ax2.legend(loc='upper right', ncol=3)
ax2.grid(True, linestyle='--', alpha=0.5)

# Optimisation et sauvegarde
plt.tight_layout()
plt.savefig('Graphique_Distinct_X_Y.png', dpi=300)
plt.show()