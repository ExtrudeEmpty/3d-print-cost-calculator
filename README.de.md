# 3D-Print Cost Calculator Pro

[🇺🇸 English version](README.md) | [🇩🇪 Deutsche Version](README.de.md)

**Die professionelle Komplettlösung für präzise Kostenkalkulation und effiziente Verwaltung deiner 3D-Druck-Projekte.**

Der 3D-Print Cost Calculator Pro wurde entwickelt, um die Lücke zwischen einfachem Slicing und wirtschaftlicher Übersicht zu schließen. Ob für engagierte Hobbyisten oder semiprofessionelle Anwender – dieses Tool bietet eine klare Kontrolle über die tatsächlichen Kostenfaktoren, die beim 3D-Druck anfallen.

---

## ✨ Hauptfunktionen

### 1. Präzise Kostenkalkulation & Preisfindung
*   **Ganzheitliche Berechnung**: Berücksichtigung von Materialverbrauch, Stromkosten, Maschinenabschreibung, Wartungskosten und Arbeitszeit.
*   **Erweiterte Energiekosten**: Differenzierte Erfassung von Drucker-Grundverbrauch, Heizbett-Leistung und Bauraumheizung.
*   **Filament-Kalibrierung**: Einzigartiges System zur Ermittlung des tatsächlichen Stromverbrauchs (Power-Factor) pro Filament-Typ für höchste Genauigkeit.
*   **Gewinnmarge & Kundenstufen**: Flexible Preisgestaltung durch hinterlegbare Margen und Arbeitszeitfaktoren für verschiedene Kundengruppen (Privat, Freunde, Business).

### 2. Umfassende Datenbankverwaltung
*   **Drucker-Flotte**: Verwaltung technischer Daten, Anschaffungskosten und erwarteter Lebensdauer zur automatischen Berechnung der Abschreibung pro Stunde.
*   **Material-Lager**: Detaillierte Materialdatenbank inklusive Dichte, Preis pro kg und spezifischer Empfehlungen für Trocknung und Bauraumheizung.
*   **Trocknungs-Management**: Integration von Trocknungsgeräten (inkl. AMS-Unterstützung) in die Stromkostenrechnung.

### 3. Kalkulations-Archiv & Kunden-Zuordnung
*   **Historie & Archiv**: Übersicht über alle gespeicherten Kalkulationen mit detaillierter Kostenaufschlüsselung zum späteren Abruf.
*   **Kunden-Zuordnung**: Hinterlegen von Kundennamen und Zuordnung zu Preisstufen für eine personalisierte Angebotserstellung.
*   **Notizen**: Speichern von spezifischen Hinweisen oder Dokumentationen zu jeder Kalkulation.

### 4. Wartungs- & Instandhaltungs-System
*   **Wartungstagebuch**: Protokollierung aller Reparaturen und Wartungen pro Drucker.
*   **Ersatzteil- & Lohnkosten**: Erfassung von Materialkosten und Arbeitsstunden für Wartungseingriffe zur Ermittlung der tatsächlichen Betriebskosten.

### 5. Modernes Interface & Technologie
*   **Premium Design**: Hochmodernes UI mit nativem Dark- und Light-Mode, anpassbaren Akzentfarben und flüssigen Mikro-Animationen.
*   **PWA-Support**: Vollwertige Installation als App auf mobilen Endgeräten mit optimierter, grid-basierter Ansicht.
*   **Globale Lokalisierung**: Unterstützung von 22 Sprachen mit einem dynamischen Übersetzungssystem für alle UI-Elemente und Metadaten.

---

## 🛠️ Technologie-Stack

*   **Backend**: Python 3.10+ mit [FastAPI](https://fastapi.tiangolo.com/) (Hochperformantes Web-Framework)
*   **Datenbank**: [PostgreSQL](https://www.postgresql.org/) (Sichere und skalierbare Datenhaltung)
*   **Frontend**: Modernes Vanilla JavaScript (ES6+), HTML5 und flexibles CSS3 (Keine schweren Frameworks für maximale Geschwindigkeit)
*   **Icons**: [Tabler Icons](https://tabler-icons.io/) für eine technische, klare Symbolik
*   **Containerisierung**: [Docker](https://www.docker.com/) & Docker Compose für einfache Bereitstellung

---

## ⚡ Schnellstart

Am schnellsten startest du das System mittels Docker Compose:

1. **Repository klonen**:
   ```bash
   git clone https://github.com/ExtrudeEmpty/3d-print-cost-calculator.git
   cd 3d-print-cost-calculator
   ```

2. **Dienste starten**:
   ```bash
   docker-compose up -d
   ```

3. **Anwendung aufrufen**:
   Öffne `http://<deine-ip>` (oder `http://localhost` bei lokaler Installation) in deinem Browser. (Standard-Port: 80)

*Hinweis: Beim ersten Start wird die Datenbank automatisch initialisiert und migriert.*

---

## 📚 Dokumentation & Mitwirkung

Detaillierte Anleitungen zur Installation, API-Dokumentation und Fehlerbehebung findest du in unserer [Vollständigen Dokumentation](docs/INDEX.md).

Du möchtest zur Weiterentwicklung beitragen? Wir freuen uns über Hilfe! Bitte beachte unsere [Contribution Guidelines](CONTRIBUTING.md) für weitere Informationen.

---

## ⚖️ Lizenz & Copyright

Dieses Projekt steht unter der **GNU Affero General Public License v3 (AGPL-3.0)**.

**Copyright (c) 2026 ExtrudeEmpty**. Alle Rechte vorbehalten.

**Credits**:
*   Icons von [Tabler Icons](https://tabler-icons.io/) (MIT Lizenz).

---

## 🎬 Hinter den Kulissen (The Making-of)

Dieses Projekt ist das Ergebnis einer ziemlich modernen Zusammenarbeit:
*   **Drehbuch & Regie**: Ein echter Mensch, der eine klare Vision verfolgte (und dabei etliche Peitschen verschliss – sei es wegen der gelegentlichen Begriffsstutzigkeit der KIs oder der Herausforderung, komplexe Visionen in binäre Logik zu übersetzen).
*   **Besetzung (Code)**: Ein Ensemble aus KIs (hauptsächlich **Gemini** und **Claude**), die fleißig getippt haben, während sie von Unmengen an virtuellem Kaffee und Strom lebten.

Keine Sorge, beim Schreiben dieses Codes wurden keine KIs dauerhaft geschädigt – auch wenn sie manchmal drei (oder zehn) Anläufe brauchten, um einen Button endlich dort zu platzieren, wo der Schöpfer ihn vorsah.

---
*Entwickelt mit ❤️ und einer Prise KI-Wahnsinn für die 3D-Druck-Community.*
