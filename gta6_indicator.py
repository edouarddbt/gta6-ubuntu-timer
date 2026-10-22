#!/usr/bin/env python3
"""
GTA 6 Countdown Indicator for Ubuntu / GNOME Top Bar.
Affiche le compte à rebours précis avant la sortie de Grand Theft Auto VI (19 novembre 2026 à minuit, heure de Paris)
dans la barre supérieure d'Ubuntu.

Optimisations batterie intégrées :
- Détection écran éteint / verrouillé (org.gnome.ScreenSaver) : pause totale du timer (0 réveil CPU).
- Détection UPower (secteur vs batterie) avec mode Auto / Éco / Perf.
- Utilisation de GLib.timeout_add_seconds pour timer-slack coalescing du noyau Linux.
- Prise en compte exacte du passage à l'heure d'hiver en France via timestamps POSIX.
"""

import sys
import os
import json
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
import zoneinfo

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

# Timezone & Target Date
PARIS_TZ = zoneinfo.ZoneInfo("Europe/Paris")
TARGET_DATE = datetime(2026, 11, 19, 0, 0, 0, tzinfo=PARIS_TZ)

CONFIG_DIR = Path.home() / ".config" / "gta6-timer"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "format_index": 0,
    "battery_mode": "auto",  # "auto", "eco", "perf"
    "icon": "input-gaming-symbolic",
}


def load_config():
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
    except Exception as e:
        print(f"Erreur chargement config: {e}", file=sys.stderr)
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print(f"Erreur sauvegarde config: {e}", file=sys.stderr)


def is_service_enabled():
    try:
        res = subprocess.run(
            ["systemctl", "--user", "is-enabled", "gta6-timer.service"],
            capture_output=True,
            text=True,
            check=False,
        )
        return res.stdout.strip() == "enabled"
    except Exception:
        return False


def toggle_service():
    try:
        currently_enabled = is_service_enabled()
        action = "disable" if currently_enabled else "enable"
        subprocess.run(["systemctl", "--user", action, "gta6-timer.service"], check=False)
        return not currently_enabled
    except Exception as e:
        print(f"Erreur toggle service: {e}", file=sys.stderr)
        return False


def compute_time_strings(format_idx=0, is_eco=False):
    now = datetime.now(PARIS_TZ)
    # L'utilisation des timestamps réels (POSIX) prend en compte le passage à l'heure d'hiver
    # en France (nuit du 25 octobre 2026 : passage de UTC+2 à UTC+1, soit 1 heure physique supplémentaire)
    total_seconds = int(TARGET_DATE.timestamp() - now.timestamp())

    if total_seconds <= 0:
        return {
            "topbar": "🎉 GTA VI EST DISPONIBLE ! 🎉",
            "full": "Le jeu est sorti !",
            "days": 0,
            "hours": 0,
            "minutes": 0,
            "seconds": 0,
            "total_seconds": 0,
        }

    days = total_seconds // 86400
    rem = total_seconds % 86400
    hours = rem // 3600
    rem = rem % 3600
    minutes = rem // 60
    seconds = rem % 60
    total_hours = total_seconds // 3600

    # Si en mode éco (batterie), le format complet s'adapte sans secondes superflues
    format_complet = (
        f"🌴 GTA VI: {days}j {hours:02d}h {minutes:02d}m"
        if is_eco
        else f"🌴 GTA VI: {days}j {hours:02d}h {minutes:02d}m {seconds:02d}s"
    )

    formats = [
        format_complet,
        f"🌴 GTA VI: {days}j {hours:02d}h {minutes:02d}m",
        f"🌴 GTA VI: {days} jours",
        f"🌴 GTA VI: {total_hours}h {minutes:02d}m {seconds:02d}s",
        f"🌴 GTA VI: {total_seconds:,}s".replace(",", " "),
    ]

    selected_format = formats[format_idx % len(formats)]
    full_str = f"{days} jours, {hours}h {minutes:02d}m {seconds:02d}s"

    return {
        "topbar": selected_format,
        "full": full_str,
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "total_seconds": total_seconds,
    }


class GTA6DBusMenu(dbus.service.Object):
    def __init__(self, bus, app):
        super().__init__(bus, "/MenuBar")
        self.app = app
        self.revision = 1

    @dbus.service.signal("com.canonical.dbusmenu", signature="ui")
    def LayoutUpdated(self, revision, parent):
        pass

    @dbus.service.method("com.canonical.dbusmenu", in_signature="iias", out_signature="u(ia{sv}av)")
    def GetLayout(self, parent_id, recursion_depth, property_names):
        is_eco = self.app.is_eco_active()
        data = compute_time_strings(self.app.config.get("format_index", 0), is_eco=is_eco)
        fmt_idx = self.app.config.get("format_index", 0)
        bat_mode = self.app.config.get("battery_mode", "auto")
        on_bat = self.app.is_on_battery()
        autostart_active = is_service_enabled()
        autostart_label = "✅ Démarrage auto avec Ubuntu : Activé" if autostart_active else "⬜ Démarrage auto avec Ubuntu : Désactivé"

        power_txt = "🔋 Sur batterie" if on_bat else "🔌 Sur secteur"

        def make_item(item_id, label, enabled=True, item_type="standard"):
            props = {
                "type": dbus.String(item_type),
                "label": dbus.String(label),
                "enabled": dbus.Boolean(enabled),
                "visible": dbus.Boolean(True),
            }
            return dbus.Struct(
                (dbus.Int32(item_id), dbus.Dictionary(props, signature="sv"), dbus.Array([], signature="v")),
                variant_level=1,
            )

        def make_sep(item_id):
            props = {
                "type": dbus.String("separator"),
                "visible": dbus.Boolean(True),
            }
            return dbus.Struct(
                (dbus.Int32(item_id), dbus.Dictionary(props, signature="sv"), dbus.Array([], signature="v")),
                variant_level=1,
            )

        items = [
            make_item(1, "🌴 Grand Theft Auto VI", enabled=False),
            make_item(2, "📅 Sortie : 19 Novembre 2026 à 00:00 (Paris)", enabled=False),
            make_item(3, f"⏳ Temps restant : {data['full']}", enabled=False),
            make_item(4, f"⚡ Total : {data['total_seconds']:,} secondes".replace(",", " "), enabled=False),
            make_item(5, "🏖️ « Trust. » — Vice City, Leonida", enabled=False),
            make_sep(6),
            make_item(7, "— Format d'affichage dans la barre —", enabled=False),
            make_item(10, f"{'●' if fmt_idx == 0 else '○'} Format Complet (jours, h, m, s)"),
            make_item(11, f"{'●' if fmt_idx == 1 else '○'} Format Compact (sans secondes)"),
            make_item(12, f"{'●' if fmt_idx == 2 else '○'} Format Jours (27 jours)"),
            make_item(13, f"{'●' if fmt_idx == 3 else '○'} Format Heures totales"),
            make_item(14, f"{'●' if fmt_idx == 4 else '○'} Format Secondes pures"),
            make_sep(15),
            make_item(16, f"— Optimisation Batterie ({power_txt}) —", enabled=False),
            make_item(17, f"{'●' if bat_mode == 'auto' else '○'} ⚡ Mode Auto (1s secteur, 30s batterie)"),
            make_item(18, f"{'●' if bat_mode == 'eco' else '○'} 🔋 Mode Éco continu (30s)"),
            make_item(19, f"{'●' if bat_mode == 'perf' else '○'} 🚀 Mode Fluide permanent (1s)"),
            make_sep(20),
            make_item(21, "🎬 Regarder le Trailer 1 (YouTube)"),
            make_item(22, autostart_label),
            make_sep(23),
            make_item(30, "❌ Fermer le timer"),
        ]

        root = (
            dbus.Int32(0),
            dbus.Dictionary({"children-display": dbus.String("submenu")}, signature="sv"),
            dbus.Array(items, signature="v"),
        )
        return dbus.UInt32(self.revision), root

    @dbus.service.method("com.canonical.dbusmenu", in_signature="aias", out_signature="a(ia{sv})")
    def GetGroupProperties(self, ids, property_names):
        return dbus.Array([], signature="(ia{sv})")

    @dbus.service.method("com.canonical.dbusmenu", in_signature="is", out_signature="v")
    def GetProperty(self, id, name):
        return dbus.String("")

    @dbus.service.method("com.canonical.dbusmenu", in_signature="isvu")
    def Event(self, item_id, event_id, data, timestamp):
        if event_id != "clicked":
            return

        if 10 <= item_id <= 14:
            new_idx = item_id - 10
            self.app.set_format(new_idx)
            self.notify_layout_updated()
        elif item_id == 17:
            self.app.set_battery_mode("auto")
            self.notify_layout_updated()
        elif item_id == 18:
            self.app.set_battery_mode("eco")
            self.notify_layout_updated()
        elif item_id == 19:
            self.app.set_battery_mode("perf")
            self.notify_layout_updated()
        elif item_id == 21:
            webbrowser.open("https://www.youtube.com/watch?v=QdBZY2fkU-0")
        elif item_id == 22:
            toggle_service()
            self.notify_layout_updated()
        elif item_id == 30:
            self.app.quit()

    @dbus.service.method("com.canonical.dbusmenu", in_signature="i", out_signature="b")
    def AboutToShow(self, item_id):
        self.notify_layout_updated()
        return dbus.Boolean(True)

    def notify_layout_updated(self):
        self.revision += 1
        self.LayoutUpdated(dbus.UInt32(self.revision), dbus.Int32(0))


class GTA6StatusNotifierItem(dbus.service.Object):
    def __init__(self, bus, app):
        super().__init__(bus, "/StatusNotifierItem")
        self.app = app
        is_eco = self.app.is_eco_active()
        data = compute_time_strings(self.app.config.get("format_index", 0), is_eco=is_eco)
        self.label = data["topbar"]

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature="ss", out_signature="v")
    def Get(self, interface, prop):
        return self.GetAll(interface).get(prop, "")

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface == "org.kde.StatusNotifierItem":
            return {
                "Category": dbus.String("ApplicationStatus"),
                "Id": dbus.String("gta6_countdown"),
                "Title": dbus.String("Compte à rebours GTA VI"),
                "Status": dbus.String("Active"),
                "IconName": dbus.String(self.app.config.get("icon", "input-gaming-symbolic")),
                "XAyatanaLabel": dbus.String(self.label),
                "XAyatanaLabelGuide": dbus.String("🌴 GTA VI: 999j 99h 99m 99s"),
                "Menu": dbus.ObjectPath("/MenuBar"),
                "ItemIsMenu": dbus.Boolean(False),
            }
        return {}

    @dbus.service.method("org.kde.StatusNotifierItem")
    def Activate(self, x, y):
        pass

    @dbus.service.signal("org.freedesktop.DBus.Properties", signature="sa{sv}as")
    def PropertiesChanged(self, interface, changed, invalidated):
        pass

    def update_label(self, new_label):
        if new_label != self.label:
            self.label = new_label
            self.PropertiesChanged(
                "org.kde.StatusNotifierItem",
                dbus.Dictionary({"XAyatanaLabel": dbus.String(self.label)}, signature="sv"),
                dbus.Array([], signature="s"),
            )


class GTA6TimerApp:
    def __init__(self):
        self.config = load_config()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SessionBus()

        self._screen_locked = False
        self._on_battery = False
        self._timeout_id = None

        self._init_power_and_screensaver()

        self.menu = GTA6DBusMenu(self.bus, self)
        self.sni = GTA6StatusNotifierItem(self.bus, self)

        # Register with watcher
        watcher = self.bus.get_object("org.kde.StatusNotifierWatcher", "/StatusNotifierWatcher")
        self.watcher_iface = dbus.Interface(watcher, "org.kde.StatusNotifierWatcher")
        self.watcher_iface.RegisterStatusNotifierItem("/StatusNotifierItem")

        self.loop = GLib.MainLoop()
        self._schedule_tick()

    def _init_power_and_screensaver(self):
        # 1. Écoute de l'état de l'écran (ScreenSaver / Lock screen)
        try:
            ss = self.bus.get_object("org.gnome.ScreenSaver", "/org/gnome/ScreenSaver")
            iface = dbus.Interface(ss, "org.gnome.ScreenSaver")
            self._screen_locked = bool(iface.GetActive())
            self.bus.add_signal_receiver(
                self._on_screensaver_changed,
                signal_name="ActiveChanged",
                dbus_interface="org.gnome.ScreenSaver",
            )
        except Exception as e:
            print(f"ScreenSaver listener non disponible: {e}", file=sys.stderr)

        # 2. Écoute de l'alimentation UPower (Secteur vs Batterie)
        try:
            self.sys_bus = dbus.SystemBus()
            upower = self.sys_bus.get_object("org.freedesktop.UPower", "/org/freedesktop/UPower")
            props = dbus.Interface(upower, "org.freedesktop.DBus.Properties")
            self._on_battery = bool(props.Get("org.freedesktop.UPower", "OnBattery"))
            self.sys_bus.add_signal_receiver(
                self._on_upower_changed,
                signal_name="PropertiesChanged",
                dbus_interface="org.freedesktop.DBus.Properties",
                path="/org/freedesktop/UPower",
            )
        except Exception as e:
            print(f"UPower listener non disponible: {e}", file=sys.stderr)

    def _on_screensaver_changed(self, active):
        self._screen_locked = bool(active)
        if self._screen_locked:
            # Écran éteint ou verrouillé -> Pause totale du timer ! 0 réveil CPU.
            if self._timeout_id:
                GLib.source_remove(self._timeout_id)
                self._timeout_id = None
        else:
            # Écran rallumé / déverrouillé -> Mise à jour instantanée et reprise
            self._on_tick()

    def _on_upower_changed(self, iface, changed, invalidated):
        if "OnBattery" in changed:
            self._on_battery = bool(changed["OnBattery"])
            self._schedule_tick()
            self._on_tick()

    def is_on_battery(self):
        return self._on_battery

    def is_eco_active(self):
        mode = self.config.get("battery_mode", "auto")
        if mode == "eco":
            return True
        if mode == "auto" and self._on_battery:
            return True
        return False

    def _schedule_tick(self):
        if self._screen_locked:
            return

        fmt = self.config.get("format_index", 0)
        is_eco = self.is_eco_active()

        # Si le format sélectionné n'a pas de secondes, ou si mode éco actif -> 30s
        interval = 30 if (fmt in (1, 2) or is_eco) else 1

        if self._timeout_id:
            GLib.source_remove(self._timeout_id)
        # GLib.timeout_add_seconds permet au noyau Linux de regrouper les réveils (timer slack)
        self._timeout_id = GLib.timeout_add_seconds(interval, self._on_tick)

    def _on_tick(self):
        if self._screen_locked:
            return False
        is_eco = self.is_eco_active()
        data = compute_time_strings(self.config.get("format_index", 0), is_eco=is_eco)
        self.sni.update_label(data["topbar"])
        self._schedule_tick()
        return False

    def set_format(self, idx):
        self.config["format_index"] = idx
        save_config(self.config)
        self._on_tick()

    def set_battery_mode(self, mode):
        self.config["battery_mode"] = mode
        save_config(self.config)
        self._on_tick()

    def quit(self):
        self.loop.quit()

    def run(self):
        self.loop.run()


def main():
    app = GTA6TimerApp()
    try:
        app.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
