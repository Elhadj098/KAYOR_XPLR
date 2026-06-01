# KAYOR XPLR - Analyse Dynamique et Cinématique

![ROS 2 Jazzy](https://img.shields.io/badge/ROS%202-Jazzy-blue)
![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04-orange)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)

Ce dépôt rassemble les outils de traitement de données, les scripts de synchronisation et le rapport d'analyse du robot mobile holonome **KAYOR XPLR** (basé sur l'architecture MentorPi M1, opérant sous ROS 2 Jazzy sur Ubuntu 24.04).

L'objectif de ce projet est de fournir un environnement complet pour étudier et comprendre les limites physiques (patinage, chocs, latence) d'une base à roues Mecanum à partir de données réelles, tout en servant de fondation pour développer des algorithmes correcteurs basés sur l'IA.

---

## Table des Matières

- [Protocole Expérimental & Architecture ROS 2](#protocole-expérimental--architecture-ros-2)
- [Résultats Clés](#résultats-clés)
- [Quick Start](#quick-start)
- [Structure du Dépôt](#structure-du-dépôt)
- [Contenu Détaillé](#contenu-détaillé)
- [Perspectives](#perspectives)
- [Installation Complète](#installation-complète)
- [Contributing](#contributing)
- [Licence](#licence)

---

## Protocole Expérimental & Architecture ROS 2

Le projet s'articule autour d'un protocole strict divisé en deux grandes phases : la capture physique distribuée sous ROS 2, puis l'analyse logicielle.

### Phase 1 : Collecte et enregistrement des flux ROS 2 (Déjà réalisée)

L'architecture logicielle embarquée repose sur l'écosystème ROS 2 Jazzy. Plusieurs nœuds computationnels s'exécutent en parallèle et publient leurs informations de manière asynchrone :

1. **Initialisation statique :** Le robot est positionné immobile sur une surface plane pendant 6,8 secondes. Le nœud de la centrale inertielle (IMU) publie le flux brut sur le topic `/imu`. Cet enregistrement de référence permet de mesurer le bruit instrumental et les biais à l'état stationnaire.

2. **Sollicitation des axes cinématiques :** Les consignes de vitesse cibles ($\pm 0,5\text{ m/s}$) sont envoyées par le nœud de navigation sous forme de messages `geometry_msgs/msg/Twist` sur le topic `/cmd_vel`. Elles couvrent tous les degrés de liberté du robot :
   * Marches avant/arrière pures (Axe X).
   * Translations latérales pures (Axe Y).
   * Pivotements (Lacet $\omega_z$) et trajectoires diagonales combinées à $45^\circ$.

3. **Estimation de l'état (Odométrie) :** Le nœud de contrôle bas niveau lit les encodeurs des moteurs, applique la matrice cinématique et publie la vitesse estimée du châssis sur le topic `/odom`.

4. **Enregistrement par Rosbag2 :** En tâche de fond, l'outil natif de journalisation est activé via la commande `ros2 bag record`. Pendant 137 secondes, il capture et sérialise l'intégralité des topics avec horodatage microseconde.

### Phase 2 : Traitement et Analyse Logicielle (Reproductible sur n'importe quel PC)

1. **Extraction des données :** Le fichier d'enregistrement ROS 2 (`.mcap`) est converti en fichiers textuels standardisés pour faciliter l'analyse hors-ligne :
   * `cmd_vel_full.csv` : Historique des consignes cinématiques.
   * `odom_full.csv` : Historique des vitesses odométriques réelles.
   * `imu_full.csv` : Historique des accélérations et vitesses angulaires (échantillonné à 50 Hz).

2. **Synchronisation temporelle :** Les topics ROS 2 publiant à des fréquences et des instants asynchrones, un script Python réaligne l'intégralité des lignes sur une grille temporelle uniforme (1 ms).

3. **Calcul des métriques :** Le script isole les écarts entre consigne et odométrie pour quantifier le patinage, mesure le décalage temporel (latence) à l'allumage, et applique un traitement statistique multi-axe.

---

## Résultats Clés

L'application de ce protocole a mis en lumière trois caractéristiques dynamiques majeures :

| Phénomène | Valeur | Impact |
|-----------|--------|--------|
| **Latence de transport** | 17,3 ms | Temps mort incompressible entre commande et réaction |
| **Patinage asymétrique (Axe Y)** | Jusqu'à 0,5 m/s | Perte d'adhérence massive lors de translations latérales |
| **Sollicitations impulsionnelles** | Pics à 2,08 G | Chocs verticaux violents dus au passage des galets |

### Interprétations Physiques

- **Latence de transport (17,3 ms) :** Temps mort incompressible mesuré entre l'émission du message sur `/cmd_vel` et la réaction physique enregistrée sur `/odom`. Critique pour les boucles de contrôle temps réel.

- **Patinage asymétrique (jusqu'à 0,5 m/s) :** Perte d'adhérence massive concentrée sur l'axe latéral (Y). La modélisation démontre que lors d'un déplacement de côté, les moteurs tournent à la vitesse commandée mais le chassis glisse. Cet effet est absent ou minimal sur l'axe X (longitudinal).

- **Sollicitations impulsionnelles (Pics à 2,08 G) :** Violents chocs verticaux enregistrés sur `/imu`. Ils proviennent du passage discontinu d'un galet à l'autre sur le sol combiné aux raccords de surface.

---

## Quick Start

### Prérequis

- Python 3.10+
- ROS 2 Jazzy
- Dépendances Python : `pandas`, `numpy`, `matplotlib`

### Utilisation Rapide

```bash
# Clone le dépôt
git clone [https://github.com/Elhadj098/KAYOR_XPLR.git](https://github.com/Elhadj098/KAYOR_XPLR.git)
cd KAYOR_XPLR

# Installe les dépendances
pip install -r requirements.txt

# Exécute l'analyse complète
python scripts/extract_data.py <chemin_vers_rosbag2.mcap>
python scripts/synchronize_data.py
python scripts/analyze_metrics.py

# Génère les graphiques
python scripts/plot_analysis.py
