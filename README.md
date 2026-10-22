<div align="center">

# 🌴 Compte à rebours GTA VI pour Ubuntu / GNOME

**Un indicateur ultra-léger et optimisé pour la batterie, affichant en temps réel le compte à rebours jusqu'à la sortie de Grand Theft Auto VI en France (19 novembre 2026 à minuit, heure de Paris) directement dans la barre supérieure d'Ubuntu.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04%20%7C%2024.04%20%7C%2026.04-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)](https://ubuntu.com/)
[![GNOME](https://img.shields.io/badge/GNOME-42%20--%2050+-4a86cf?style=for-the-badge&logo=gnome&logoColor=white)](https://www.gnome.org/)
[![Licence: MIT](https://img.shields.io/badge/Licence-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Optimisé Batterie](https://img.shields.io/badge/Batterie-Optimis%C3%A9e-success?style=for-the-badge&logo=leaf&logoColor=white)](#-gestion-intelligente-de-la-batterie)

```text
+---------------------------------------------------------------------------------------------------+
| Activités        [  20:45  ]                      [🎮 🌴 GTA VI: 27j 04h 28m]  [🔋 85%] [📶] [🔊] |
+---------------------------------------------------------------------------------------------------+
```

[Fonctionnalités](#-fonctionnalités) • [Installation](#-installation-rapide) • [Commandes CLI](#-commandes-utiles-cli) • [Optimisation Batterie](#-gestion-intelligente-de-la-batterie) • [Architecture](#-fonctionnement-technique) • [Désinstallation](#-désinstallation)

</div>

---

## ✨ Fonctionnalités

- 🎮 **Intégration native dans la barre du haut** : icône manette discrète et décompte en temps réel via le standard Freedesktop `StatusNotifierItem` (utilisé par l'extension AppIndicators d'Ubuntu).
- ⏱️ **Précision physique absolue (Heure d'hiver)** : calcul basé sur les timestamps POSIX pour intégrer exactement le passage à l'heure d'hiver en France (+1 heure physique réelle durant la nuit de 25 heures fin octobre).
- 🔋 **Zéro impact sur l'autonomie** :
  - Adaptation dynamique selon l'alimentation : **1s** sur secteur, **30s** sur batterie via `org.freedesktop.UPower`.
  - **Mise en pause totale** dès que l'écran est éteint ou verrouillé (`org.gnome.ScreenSaver`), garantissant **0 réveil CPU**.
  - Empreinte ultra-faible : **< 0,05 % CPU** et **~20 Mo de RAM**.
- 🖱️ **Menu déroulant interactif au clic** :
  - Statistiques complètes en direct (jours, heures, minutes, secondes et total de secondes restantes).
  - Changement de format à la volée (*Complet avec secondes, Compact, Jours seuls, Heures totales, Secondes brutes*).
  - Raccourci vers le Trailer 1 officiel de Rockstar Games sur YouTube.
  - Bascule du démarrage automatique en 1 clic.
- 🚀 **Gestion par service systemd utilisateur** : service d'arrière-plan autonome (`systemd --user`) qui démarre automatiquement à l'ouverture de session et se relance en cas d'erreur.

---

## 🚀 Installation rapide

Clone le dépôt et lance le script d'installation :

```bash
git clone https://github.com/edouarddbt/gta6-ubuntu-timer.git
cd gta6-ubuntu-timer
chmod +x install.sh
./install.sh
```

> **Prérequis** : Ubuntu ou distribution basée sur Debian avec GNOME Shell et Python 3 (présents par défaut sur Ubuntu).

---

## 💻 Commandes utiles (CLI)

Tu peux piloter le timer à tout moment depuis ton terminal grâce à la commande `gta6-timer` :

```bash
# Consulter le temps restant et l'état du service
gta6-timer status

# Démarrer le timer dans la barre supérieure
gta6-timer start

# Arrêter le timer
gta6-timer stop

# Redémarrer le service
gta6-timer restart

# Activer / Désactiver le lancement automatique au démarrage
gta6-timer enable
gta6-timer disable

# Lancer en direct au premier plan (mode debug)
gta6-timer run
```

---

## 🔋 Gestion intelligente de la batterie

De nombreuses applications réveillent le processeur chaque seconde, ce qui empêche le CPU de basculer dans ses états d'économie d'énergie profonde (*deep C-states*). Cet indicateur a été conçu pour être totalement invisible sur l'autonomie :

| Situation / Mode | Comportement | Réveils processeur |
| :--- | :--- | :--- |
| **🔌 Sur secteur (AC)** | Défilement fluide seconde par seconde | Normal (~1 Hz) |
| **🔋 Sur batterie (Auto)** | Intervalle automatique espacé à 30 secondes | **-96,7 % de réveils** |
| **🔒 Écran verrouillé / éteint** | Pause totale du timer | **0 réveil (sommeil complet)** |
| **⚡ Coalescing noyau Linux** | Utilisation de `GLib.timeout_add_seconds` pour regrouper les interruptions | Réveils synchronisés |

Tu peux également forcer le profil d'énergie directement depuis le menu au clic :
- **Mode Auto** *(Recommandé)* : 1s sur secteur, 30s sur batterie.
- **Mode Éco** : 30s en continu.
- **Mode Fluide** : 1s en continu.

---

## 🧠 Fonctionnement technique

L'indicateur communique directement avec GNOME Shell sans couche lourde (pas d'Electron ni de navigateur web embarqué) :

```text
+---------------------------------------------------------------+
|                      gta6_indicator.py                        |
+-------------------------------+-------------------------------+
                                |
               D-Bus IPC        |       D-Bus IPC
      (org.kde.StatusNotifier)  |  (org.freedesktop.UPower / ScreenSaver)
                                v
+-------------------------------+-------------------------------+
|     ubuntu-appindicators      |     Barre supérieure GNOME    |
|   (StatusNotifierWatcher)     |  "🌴 GTA VI: 27j 04h 28m"     |
+-------------------------------+-------------------------------+
```

- **`gta6_indicator.py`** : Exporte les objets D-Bus `org.kde.StatusNotifierItem` et `com.canonical.dbusmenu`.
- **`systemd --user`** : Supervise le cycle de vie du processus en arrière-plan.
- **`gta6-timer`** : Script utilitaire Bash pour dialoguer facilement avec `systemctl --user`.

---

## 🗑️ Désinstallation

Pour supprimer proprement le timer, son service et ses raccourcis :

```bash
./uninstall.sh
```

---

## 📜 Licence

Projet publié sous licence [MIT](LICENSE).
N'hésite pas à laisser une étoile ⭐ sur le repo si tu attends GTA VI !
