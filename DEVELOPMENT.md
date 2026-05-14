# Development & Localization Rules / Entwicklungs- & Lokalisierungsregeln

This document outlines the core development principles for this project.
Dieses Dokument beschreibt die zentralen Entwicklungsprinzipien für dieses Projekt.

---

## English

### 1. Localization (L10n)
- **Rule:** Whenever a key is added, removed, or modified in any language file, **ALL 22 languages** must be updated simultaneously.
- **Main Files:** `backend/app/static/locales/de.json`, `backend/app/static/locales/en.json`
- **Additional Files:** All files in `backend/app/static/locales/additional/*.json`
- **Consistency:** All JSON files must be kept alphabetically sorted by key.
- **Technical Terms:** Technical terms must remain technically accurate and consistent across all translations.

### 2. Terminology Policy
- **Heated Bed:** "Independent Heatbed" (EN) / "Autarkes Heizbett" (DE). This refers specifically to beds not powered by the main PSU.
- **Labor:** Use "Labor Factor" (EN) / "Arbeitsfaktor" (DE) instead of generic "Time Factor".
- **Costs:** Use "Base Costs" (EN) / "Selbstkosten" (DE) for technical cost calculations.

### 3. Deployment & History
- **Stealth Updates:** When fixing terminology regressions or minor bugs, use `git commit --amend` to keep the history clean of "fix translation" noise.
- **Release:** Use `release.sh <version> ["description"]` to update the public repository.

---

## Deutsch

### 1. Lokalisierung (L10n)
- **Regel:** Sobald ein Schlüssel in einer Sprachdatei hinzugefügt, entfernt oder geändert wird, müssen **ALLE 22 Sprachen** gleichzeitig aktualisiert werden.
- **Hauptdateien:** `backend/app/static/locales/de.json`, `backend/app/static/locales/en.json`
- **Zusätzliche Dateien:** Alle Dateien in `backend/app/static/locales/additional/*.json`
- **Konsistenz:** Alle JSON-Dateien müssen alphabetisch nach Schlüsseln sortiert bleiben.
- **Fachbegriffe:** Technische Begriffe müssen präzise und über alle Übersetzungen hinweg konsistent bleiben.

### 2. Terminologie-Richtlinien
- **Heizbett:** "Independent Heatbed" (EN) / "Autarkes Heizbett" (DE). Dies bezieht sich speziell auf Betten, die nicht über das Hauptnetzteil des Druckers versorgt werden.
- **Arbeit:** Verwende "Labor Factor" (EN) / "Arbeitsfaktor" (DE) anstelle des generischen "Zeitfaktors".
- **Kosten:** Verwende "Base Costs" (EN) / "Selbstkosten" (DE) für technische Kostenkalkulationen.

### 3. Deployment & Historie
- **Stealth Updates:** Bei der Korrektur von Terminologie-Regressionsfehlern oder kleineren Bugs sollte `git commit --amend` verwendet werden, um die Historie sauber von "Übersetzungsfix"-Rauschen zu halten.
- **Release:** Verwende `release.sh <version> ["beschreibung"]`, um das öffentliche Repository zu aktualisieren.
