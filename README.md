# 🌴 GTA 6 Top Bar Countdown for Ubuntu / GNOME

Un indicateur stylé et ultra-léger pour la barre supérieure d'Ubuntu (GNOME), affichant le compte à rebours en temps réel jusqu'à la sortie de **Grand Theft Auto VI en France** (**19 novembre 2026 à minuit, heure de Paris**).

---

## ✨ Fonctionnalités

- **Affichage en direct dans la barre du haut** : icône manette Yaru + compte à rebours précis qui s'actualise chaque seconde (`🌴 GTA VI: 29j 08h 10m 48s`).
- **Menu déroulant complet au clic** :
  - 🌴 Nom complet : *Grand Theft Auto VI*
  - 📅 Date officielle : *19 Novembre 2026 à 00:00:00 (Paris)*
  - ⏳ Temps restant en direct (jours, heures, minutes, secondes)
  - ⚡ Nombre total de secondes restantes
  - 🏖️ Citation de Vice City
  - ⚙️ **Choix du format d'affichage** en un clic :
    - `Complet` : `29j 08h 10m 48s`
    - `Compact` : `29j 08h 10m`
    - `Jours` : `29 jours`
    - `Heures totales` : `652h...`
    - `Secondes pures` : `2 349 144s`
  - 🔋 **Optimisations Batterie intelligentes** :
    - `Mode Auto` : fluide (1s) sur secteur, économique (30s) sur batterie.
    - `Mode Éco` : 30s en continu.
    - `Mode Fluide` : 1s en continu.
    - `Pause écran éteint / verrouillé` : 0 réveil CPU quand l'écran est en veille ou verrouillé.
  - 🎬 Raccourci vers le Trailer officiel sur YouTube
  - 🔄 Activation / Désactivation du démarrage automatique
  - ❌ Option pour fermer le timer
- **Intégration native Ubuntu** : Utilise le protocole standard AppIndicator / StatusNotifierItem (intégré par défaut dans Ubuntu) ainsi qu'un service utilisateur `systemd`.
- **Démarrage automatique** : S'exécute automatiquement à chaque ouverture de session.

---

## 🚀 Commandes utiles

Tu peux gérer le timer depuis n'importe quel terminal avec la commande `gta6-timer` :

```bash
# Vérifier l'état du service et le temps restant
gta6-timer status

# Arrêter le timer
gta6-timer stop

# Démarrer le timer
gta6-timer start

# Redémarrer le timer
gta6-timer restart

# Activer/Désactiver le démarrage automatique avec Ubuntu
gta6-timer enable
gta6-timer disable
```

---

## 📂 Structure des fichiers

- [`gta6_indicator.py`](file:///home/edouard/Documents/antigravity/beautiful-goodall/gta6_indicator.py) : Script Python principal (DBus / AppIndicator / StatusNotifierItem).
- [`gta6-timer`](file:///home/edouard/Documents/antigravity/beautiful-goodall/gta6-timer) : CLI de contrôle (`start`, `stop`, `status`, etc.).
- [`gta6-timer.service`](file:///home/edouard/Documents/antigravity/beautiful-goodall/gta6-timer.service) : Unité systemd utilisateur pour la persistance et le redémarrage automatique.
- [`install.sh`](file:///home/edouard/Documents/antigravity/beautiful-goodall/install.sh) : Script d'installation automatique.
- [`uninstall.sh`](file:///home/edouard/Documents/antigravity/beautiful-goodall/uninstall.sh) : Script de désinstallation propre.
- Companion GNOME Extension : situé dans `~/.local/share/gnome-shell/extensions/gta6-timer@edouard/`.
