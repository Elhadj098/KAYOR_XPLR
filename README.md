# KAYOR XPLR - Analyse Dynamique et Cinématique

Ce dépôt rassemble les outils de traitement de données, les scripts de synchronisation et le rapport d'analyse du robot mobile holonome **KAYOR XPLR** (basé sur l'architecture MentorPi M1, opérant sous ROS 2 Jazzy et Ubuntu 24.04). 

L'objectif de ce projet est de fournir un environnement complet pour étudier et comprendre les limites physiques (patinage, chocs, latence) d'une base à roues Mecanum à partir de données réelles. **Il n'est pas nécessaire de posséder le robot pour utiliser ce dépôt** ; des jeux de données d'essais sont inclus pour exécuter les analyses.

## Protocole Expérimental & Architecture ROS 2

Le projet s'articule autour d'un protocole strict divisé en deux grandes phases : la capture physique distribuée sous ROS 2, puis l'analyse logicielle.

### Phase 1 : Collecte et enregistrement des flux ROS 2 (Déjà réalisée)
L'architecture logicielle embarquée repose sur l'écosystème ROS 2 Jazzy. Plusieurs nœuds computationnels s'exécutent en parallèle et publient leurs informations de manière asynchrone :
1. **Initialisation statique :** Le robot est positionné immobile sur une surface plane pendant 6,8 secondes. Le nœud de la centrale inertielle (IMU) publie le flux brut sur le topic `/imu`. Cette phase permet d'isoler le bruit de fond et d'établir le vecteur gravité de référence.
2. **Sollicitation des axes cinématiques :** Les consignes de vitesse cibles ($\pm 0,5\text{ m/s}$) sont envoyées par le nœud de navigation sous forme de messages `geometry_msgs/msg/Twist` sur le topic `/cmd_vel`. Les mouvements alternent :
   * Marches avant/arrière pures (Axe X).
   * Translations latérales pures (Axe Y).
   * Pivotements (Lacet $\omega_z$) et trajectoires diagonales combinées à $45^\circ$.
3. **Estimation de l'état (Odométrie) :** Le nœud de contrôle bas niveau lit les encodeurs des moteurs, applique la matrice cinématique et publie la vitesse estimée du châssis sur le topic `/odom` (messages `nav_msgs/msg/Odometry`).
4. **Enregistrement par Rosbag2 :** En tâche de fond, l'outil natif de journalisation est activé via la commande `ros2 bag record`. Pendant 137 secondes, il capture et sérialise l'intégralité des messages circulant sur `/cmd_vel`, `/odom` et `/imu` sans interférer avec la boucle de contrôle temps réel.

### Phase 2 : Traitement et Analyse Logicielle (Reproductible sur n'importe quel PC)
1. **Extraction des données :** Le fichier d'enregistrement ROS 2 (`.db3` ou `.mcap`) est converti en fichiers textuels standardisés pour faciliter l'analyse hors-ligne :
   * `cmd_vel_full.csv` : Historique des consignes cinématiques.
   * `odom_full.csv` : Historique des vitesses odométriques réelles.
   * `imu_full.csv` : Historique des accélérations et vitesses angulaires (échantillonné à 50 Hz).
2. **Synchronisation temporelle :** Les topics ROS 2 publiant à des fréquences et des instants asynchrones, un script Python réaligne l'intégralité des lignes sur une grille temporelle uniforme à 100 Hz ($t_0 = 0\text{ s}$ calé sur le premier message de commande reçu).
3. **Calcul des métriques :** Le script isole les écarts entre consigne et odométrie pour quantifier le patinage, mesure le décalage temporel (latence) à l'allumage, et applique un traitement sur l'accélération $Z$ pour quantifier l'intensité des chocs mécaniques.

## Résumé des Phénomènes Physiques Identifiés
L'application de ce protocole a mis en lumière trois caractéristiques dynamiques majeures :
* **Latence de transport (17,3 ms) :** Temps mort incompressible mesuré entre l'émission du message sur `/cmd_vel` et la réaction physique enregistrée sur `/odom`.
* **Patinage asymétrique (jusqu'à 0,5 m/s) :** Perte d'adhérence massive concentrée sur l'axe latéral (Y). La modélisation démontre que lors d'un déplacement de côté, les moteurs tournent en opposition forcée à travers la structure rigide, poussant les galets au-delà de leur limite d'adhérence.
* **Sollicitations impulsionnelles (Pics à 2,08 G) :** Violents chocs verticaux enregistrés sur `/imu`. Ils proviennent du passage discontinu d'un galet à l'autre sur le sol combiné aux raccrochages brutaux d'adhérence en fin de glissement.

## Contenu du Dépôt
* **Rapport\_Analyse.pdf :** Le rapport d'ingénierie complet détaillant les calculs, le développement de la pseudo-inverse de Moore-Penrose pour le modèle cinématique, et l'interprétation des résultats.
* **Graphique\_Distinct\_X\_Y.png :** Le visuel généré montrant la superposition parfaite sur l'axe X et le décrochage du patinage sur l'Axe Y.
* **Scripts Python :** Les codes sources de traitement utilisant `pandas`, `numpy` et `matplotlib`.

##  Perspectives
Ce protocole et les données associées servent de base de connaissances pour entraîner et valider un algorithme correcteur par Intelligence Artificielle (IA), dont le but sera de lisser les commandes du topic `/cmd_vel` afin d'annuler le patinage et de protéger la structure des chocs à forte dynamique.
