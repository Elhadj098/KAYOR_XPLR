import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Chargement et synchronisation des données
cmd = pd.read_csv('cmd_vel_full.csv')
odom = pd.read_csv('odom_full.csv')
imu = pd.read_csv('imu_full.csv')

min_ts = min(cmd['timestamp_ns'].min(), odom['timestamp_ns'].min(), imu['timestamp_ns'].min())

cmd['time'] = (cmd['timestamp_ns'] - min_ts) / 1e9
odom['time'] = (odom['timestamp_ns'] - min_ts) / 1e9
imu['time'] = (imu['timestamp_ns'] - min_ts) / 1e9

# Interpolation sur une grille commune à 100 Hz
t_min = max(cmd['time'].min(), odom['time'].min(), imu['time'].min())
t_max = min(cmd['time'].max(), odom['time'].max(), imu['time'].max())
time_grid = np.linspace(t_min, t_max, num=int((t_max - t_min) * 100))

df = pd.DataFrame({'time': time_grid})
df['cmd_x'] = np.interp(time_grid, cmd['time'], cmd['linear_x'])
df['cmd_y'] = np.interp(time_grid, cmd['time'], cmd['linear_y'])
df['vel_x'] = np.interp(time_grid, odom['time'], odom['vel_x'])
df['vel_y'] = np.interp(time_grid, odom['time'], odom['vel_y'])
df['pos_x'] = np.interp(time_grid, odom['time'], odom['pos_x'])
df['pos_y'] = np.interp(time_grid, odom['time'], odom['pos_y'])
df['accel_z'] = np.interp(time_grid, imu['time'], imu['accel_z'])

# 2. Génération et sauvegarde des graphiques

# Graphique 1 : Fidélité X
plt.figure(figsize=(10, 5))
plt.plot(df['time'], df['cmd_x'], label='Consigne (cmd_vel.linear_x)', alpha=0.8)
plt.plot(df['time'], df['vel_x'], label='Réel (odom.vel_x)', alpha=0.8)
plt.xlabel('Temps (s)')
plt.ylabel('Vitesse X (m/s)')
plt.title('Fidélité Moteur - Axe X (Frontal)')
plt.legend()
plt.grid()
plt.savefig('fidelity_x.png', bbox_inches='tight')
plt.close()

# Graphique 2 : Fidélité Y
plt.figure(figsize=(10, 5))
plt.plot(df['time'], df['cmd_y'], label='Consigne (cmd_vel.linear_y)', alpha=0.8)
plt.plot(df['time'], df['vel_y'], label='Réel (odom.vel_y)', alpha=0.8)
plt.xlabel('Temps (s)')
plt.ylabel('Vitesse Y (m/s)')
plt.title('Fidélité Moteur - Axe Y (Latéral)')
plt.legend()
plt.grid()
plt.savefig('fidelity_y.png', bbox_inches='tight')
plt.close()

# Graphique 3 : Vitesse X vs Vibrations
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(df['time'], df['vel_x'], color='tab:blue', label='Vitesse X')
ax1.set_xlabel('Temps (s)')
ax1.set_ylabel('Vitesse X (m/s)', color='tab:blue')
ax2 = ax1.twinx()
ax2.plot(df['time'], df['accel_z'], color='tab:red', alpha=0.5, label='Accel Z')
ax2.axhline(15, color='orange', linestyle='--', label='Seuil Choc (15 m/s²)')
ax2.axhline(-15, color='orange', linestyle='--')
ax2.set_ylabel('Accélération Z (m/s²)', color='tab:red')
plt.title('Vitesse Frontale vs Vibrations')
fig.tight_layout()
plt.savefig('speed_vs_vib.png', bbox_inches='tight')
plt.close()

# Graphique 4 : Vitesse Y vs Vibrations
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(df['time'], df['vel_y'], color='tab:green', label='Vitesse Y')
ax1.set_xlabel('Temps (s)')
ax1.set_ylabel('Vitesse Y (m/s)', color='tab:green')
ax2 = ax1.twinx()
ax2.plot(df['time'], df['accel_z'], color='tab:red', alpha=0.5)
ax2.axhline(15, color='orange', linestyle='--')
ax2.axhline(-15, color='orange', linestyle='--')
ax2.set_ylabel('Accélération Z (m/s²)', color='tab:red')
plt.title('Vitesse Latérale vs Vibrations')
fig.tight_layout()
plt.savefig('speed_y_vs_vib.png', bbox_inches='tight')
plt.close()

# Graphique 5 : Vitesses X et Y combinées vs Vibrations
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(df['time'], df['vel_x'], color='tab:blue', label='Vitesse X (Frontale)')
ax1.plot(df['time'], df['vel_y'], color='tab:green', label='Vitesse Y (Latérale)')
ax1.set_xlabel('Temps (s)')
ax1.set_ylabel('Vitesse (m/s)', color='black')
ax1.legend(loc='upper left')
ax2 = ax1.twinx()
ax2.plot(df['time'], df['accel_z'], color='tab:red', alpha=0.3)
ax2.axhline(15, color='orange', linestyle='--')
ax2.axhline(-15, color='orange', linestyle='--')
ax2.set_ylabel('Accélération Z (m/s²)', color='tab:red')
plt.title('Impact des mouvements combinés (X et Y) sur l\'accélération Z')
fig.tight_layout()
plt.savefig('speed_xy_vs_vib.png', bbox_inches='tight')
plt.close()

# Graphique 6 : Trajectoire
plt.figure(figsize=(8, 8))
plt.plot(df['pos_x'], df['pos_y'], label='Trajectoire', color='blue')
plt.scatter(df['pos_x'].iloc[0], df['pos_y'].iloc[0], color='green', s=100, label='Départ', zorder=5)
plt.scatter(df['pos_x'].iloc[-1], df['pos_y'].iloc[-1], color='red', s=100, label='Arrivée', zorder=5)
plt.xlabel('Position X (m)')
plt.ylabel('Position Y (m)')
plt.title('Tracé XY du déplacement (Odométrie)')
plt.legend()
plt.grid()
plt.axis('equal')
plt.savefig('trajectory.png', bbox_inches='tight')
plt.close()

print("Tous les graphiques ont été générés et sauvegardés avec succès dans le dossier courant.")