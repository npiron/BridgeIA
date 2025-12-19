# BridgeIA

Prototype de jeu de construction de ponts (type "Poly Bridge") alimenté par une IA, développé en Python avec Pygame et Pymunk.

## Fonctionnalités

- **Construction Libre** : Créez des joints et des segments de pont où vous voulez (respectant la longueur maximale).
- **Simulation Physique** : Testez la stabilité de votre pont avec un moteur physique réaliste (gravité, contraintes).
- **Interface Intuitive** : Mode construction et mode simulation avec grille aimantée.

## Prérequis

Pour lancer ce projet localement, vous avez besoin de :

- **Python 3.11** ou supérieur
- **Poetry** (Gestionnaire de dépendances Python)

## Installation et Lancement

### Démarrage Rapide

1. Rendez le script exécutable :
   ```bash
   chmod +x run_local.sh
   ```

2. Lancez le jeu :
   ```bash
   ./run_local.sh
   ```

## Contrôles

| Action | Touche / Commande |
|--------|-------------------|
| **Sélectionner / Construire** | Clic Gauche (sur ancre ou dans le vide pour créer un joint) |
| **Supprimer** | Clic Droit (sur segment ou joint) |
| **Annuler Sélection** | Échap (ESC) |
| **Lancer / Arrêter Simulation** | Espace (SPACE) |
| **Activer/Désactiver Grille** | G |
| **Ajuster Taille Grille** | `[` et `]` (ou touches adjacentes) |

### Astuces de jeu
- Utilisez la grille pour aligner parfaitement vos triangles.
- Si le curseur "snappe" (saute) sur la grille, vous pouvez être sûr de la position.
- Les points existants sont prioritaires sur la grille : si vous cliquez près d'un point, vous le sélectionnerez.
