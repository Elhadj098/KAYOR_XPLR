import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Chargement des données
cmd = pd.read_csv('cmd_vel_full.csv')
odom = pd.read_csv('odom_full.csv')

# Synchronisation temporelle
min_ts = min(cmd['timestamp_ns'].min(), odom['timestamp_ns'].min())
cmd['time'] = (cmd['timestamp_ns'] - min_ts) / 1e9
odom['time'] = (odom['timestamp_ns'] - min_ts) / 1e9

# Identification du saut (Consigne à 0,058 m/s)
t_jump = cmd[cmd['linear_x'] > 0.01]['time'].iloc[0]
v_target = 0.058

# Fenêtre de zoom (200 ms)
t_start, t_end = t_jump - 0.05, t_jump + 0.15
df_cmd_micro = cmd[(cmd['time'] >= t_start) & (cmd['time'] <= t_end)]
df_odom_micro = odom[(odom['time'] >= t_start) & (odom['time'] <= t_end)]

plt.figure(figsize=(10, 6))

# Plot des courbes
plt.step(df_cmd_micro['time'], df_cmd_micro['linear_x'], label='Consigne (X)', where='post', color='blue', marker='o')
plt.plot(df_odom_micro['time'], df_odom_micro['vel_x'], label='Réponse Réelle (X)', color='orange', marker='x')

# Ajout de la valeur 0,058 m/s sur le graphe
plt.axhline(y=v_target, color='blue', linestyle=':', alpha=0.6)
plt.text(t_start + 0.01, v_target + 0.002, f'Vitesse : {v_target} m/s', color='blue', fontweight='bold')

# Marquage de la latence de 20 ms
t_resp = t_jump + 0.02
plt.annotate('', xy=(t_resp, 0.03), xytext=(t_jump, 0.03),
             arrowprops=dict(arrowstyle='<->', color='red', lw=2))
plt.text((t_jump + t_resp)/2, 0.035, '$\Delta t = 20$ ms', color='red', ha='center', fontweight='bold')

# Grille de précision (10 ms)
plt.gca().xaxis.set_minor_locator(plt.MultipleLocator(0.01))
plt.grid(which='minor', linestyle=':', alpha=0.5)
plt.grid(which='major', alpha=0.3)

plt.title('Caractérisation du retard système ($\Delta t = 20$ ms)')
plt.xlabel('Temps (s)')
plt.ylabel('Vitesse (m/s)')
plt.legend()

plt.savefig('micro_latency_proof.png', bbox_inches='tight')