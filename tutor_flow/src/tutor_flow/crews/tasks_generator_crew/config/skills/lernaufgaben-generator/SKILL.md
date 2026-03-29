---
name: lernaufgaben-generator
description: >
  Erstellt druckfertige Lernaufgaben und Übungsblätter für die Mittelstufe (Klasse 5–9) passend zu den Lehrplänen in Deutschland, Österreich und der Schweiz. Verwende diesen Skill immer wenn der Benutzer Aufgaben, Übungsblätter, Tests, Vokabelübungen, Grammatikübungen, Übersetzungstexte oder Rechtschreibtests erstellen möchte — auch wenn hochgeladene Inhalte (PDF, Bild, Vokabelliste, Grammatikregeln) als Basis dienen sollen. Trigger auch bei Begriffen wie "Lernaufgabe", "Arbeitsblatt", "Vokabeltest", "Übungsblatt", "Klassenarbeit vorbereiten" oder "Aufgaben für Schüler". Ausgabe sind zwei Dateien im Markdown-Format: Aufgabenblatt und separater Lösungsschlüssel.
---

# Lernaufgaben-Generator

Erstellt strukturierte, lehrplangerechte Aufgabenblätter für die Mittelstufe (Klasse 5–9, DE/AT/CH) als druckfertige Markdown-Dateien.

---

## Workflow

### Schritt 1: Eingabe verstehen

Der Benutzer kann Inhalte auf vier Arten liefern:

- **Bereits importierte Vokabeln aus dem Flow-Kontext**: Wenn `import_vocabulary_task` bereits eine strukturierte Vokabelliste geliefert hat, verwende diese **immer zuerst** als primäre Datenquelle.
  Nutze die Felder `subject`, `lessons`, `source_files` und `entries` direkt aus dem Kontext.
- **Dateizugriff nur als Fallback**: Nutze den `Vocabulary library file reader` nur dann, wenn keine verwertbare Import-Liste vorliegt oder wichtige Eintraege fehlen.
  Bevorzuge dann passende Dateien unter `src/tutor_flow/vocabulary_library/` fuer das ausgewaehlte Fach und die ausgewaehlten Lektionen.
- **Hochgeladene Datei** (PDF oder Bild): Lese/extrahiere den Inhalt mit geeignetem Tool und identifiziere Vokabeln, Grammatikregeln oder Texte.
- **Text im Chat**: Direkt als Vokabelliste, Regelauflistung oder Fließtext.
- **Kein Inhalt**: Generiere passende Aufgaben basierend auf Fach, Klasse und Aufgabentyp.

#### Fallback-Vokabelbibliothek

Falls kein brauchbarer Import-Kontext vorhanden ist, verwende `src/tutor_flow/vocabulary_library/`.
Nutze fuer Latein Dateien wie `latin/prima_lektionXX.md` und fuer Englisch Dateien wie `english/greenline_unitXX.md`.

**Fehlende Informationen abfragen (falls nicht angegeben):**
1. Fach (z.B. Latein, Englisch, Deutsch)
2. Klasse (5–9)
3. Aufgabentyp (siehe unten)
4. Lösungsschlüssel gewünscht? (Standard: Ja, am Ende)

### Schritt 2: Aufgabentyp wählen

| Typ | Beschreibung | Einsatz |
|-----|-------------|---------|
| `vokabeltest` | Vokabeln Zielsprache → Deutsch oder umgekehrt, Lücken oder Zuordnung | Latein, Englisch, Französisch |
| `uebersetzung` | Sätze oder kurzer Text zur Übersetzung | Latein, Englisch |
| `grammatik` | Formenbildung, Deklinationstabellen, Konjugationen, Lückentexte | Alle Sprachen |
| `rechtschreibung` | Lückentext, Fehlersuche, Diktatsätze mit Fokuswort | Deutsch |
| `leseverstehen` | Text + Verständnisfragen | Englisch, Deutsch |
| `gemischt` | Kombination mehrerer Typen | Beliebig |

### Schritt 3: Aufgaben generieren

Verwende fuer sprachbezogene Aufgaben (Latein/Englisch) zuerst die importierten `entries` aus `import_vocabulary_task`.
Fuehre Dateizugriff nur im Fallback aus und dokumentiere in der Ausgabe kurz, welche Quelle verwendet wurde.

**Qualitätskriterien:**
- Altersgerecht: Wortschatz und Komplexität für Klasse 7
- Lehrplanorientiert: Inhalte orientieren sich an den Kerncurricula DE/AT/CH
- Klar strukturiert: Nummerierte Aufgaben, verständliche Anweisungen
- Angemessener Umfang: ca. 10–15 Minuten Bearbeitungszeit (sofern nicht anders gewünscht)

**Aufgabenbau je nach Typ:**

*Vokabeltest:*
- Tabelle: Spalte Zielsprache | Spalte Deutsch (eine leer lassen)
- Oder: Nummerierte Liste mit Lücken
- Mind. 10–15 Vokabeln

*Übersetzung:*
- 5–10 Einzelsätze oder 1 kurzer Text (80–150 Wörter)
- Schwierigkeit angepasst an Klasse und Vokabular

*Grammatikübung:*
- Erklärungskasten mit der Regel (falls gewünscht)
- Lückentext, Formentabelle zum Ausfüllen, oder Umformungsaufgaben

*Rechtschreibung:*
- Fokuswörter klar benennen (z.B. "Groß-/Kleinschreibung", "ie/ei", "ss/ß")
- Fehlersuche, Lückentext oder Diktatsätze

### Schritt 4: Markdown im festen Template erstellen

Erzeuge **zwei getrennte Markdown-Dateien**:

1. Aufgabenblatt (ohne Lösungen)
2. Lösungsschlüssel (nur Lösungen)

Verwende für das Aufgabenblatt immer dieses Template:

```markdown
# {titel}

**Fach:** {fach}  
**Klasse:** {klasse}  
**Lektionen:** {lektionen}  
**Aufgabentyp:** {typ}  
**Datum:** ____________  
**Name:** ___________________________

---

## Arbeitsauftrag
{kurze_anweisung_fuer_schueler}

## Aufgaben

### Aufgabe 1
{aufgabeninhalt_ohne_loesung}

### Aufgabe 2
{aufgabeninhalt_ohne_loesung}

### Aufgabe 3
{optional_weitere_aufgaben}

---

## Hinweise
{optionale_hinweise_oder_vokabelhilfe_ohne_loesungen}
```

Verwende für den Lösungsschlüssel immer dieses Template:

```markdown
# Lösungsschlüssel - {titel}

**Fach:** {fach}  
**Klasse:** {klasse}  
**Lektionen:** {lektionen}  
**Aufgabentyp:** {typ}

---

## Lösungen

### Aufgabe 1 - Lösung
{loesung_zu_aufgabe_1}

### Aufgabe 2 - Lösung
{loesung_zu_aufgabe_2}

### Aufgabe 3 - Lösung
{loesung_zu_aufgabe_3}
```

Regeln:
- Im Aufgabenblatt niemals Musterlösungen oder direkte Antworten ausgeben.
- Alle Lösungen ausschließlich in der separaten Lösungsdatei.
- Die Nummerierung der Aufgaben muss zwischen beiden Dateien exakt übereinstimmen.

### Schritt 5: Strukturierte Ausgabe (verbindlich)

Gib am Ende **nur ein JSON-Objekt** zurueck (keinen Fliesstext, keine Erklaerung, keine Markdown-Codefences).

Verwende exakt dieses Schema:

```json
{
  "worksheet_markdown": "<vollstaendiger Markdown-Inhalt des Aufgabenblatts>",
  "solution_markdown": "<vollstaendiger Markdown-Inhalt des Loesungsschluessels>",
  "worksheet_path": "aufgaben/[fach]/aufgabenblatt_[fach]_[typ].md",
  "solution_path": "aufgaben/[fach]/aufgabenblatt_[fach]_[typ]_loesung.md"
}
```

Regeln fuer das JSON:
- `worksheet_markdown` und `solution_markdown` sind Pflichtfelder und muessen Strings sein.
- `worksheet_path` und `solution_path` sind Pflichtfelder und muessen relative Pfade sein.
- Keine zusaetzlichen Top-Level-Felder ausgeben.
- Keine Kommentare, keine Backticks, kein Text vor oder nach dem JSON.

---

## Beispiel-Prompts (Trigger)

- „Erstelle einen Vokabeltest für Latein Klasse 6 mit diesen Vokabeln: [Liste]"
- „Mach ein Übungsblatt zur Adjektivdeklination auf Deutsch für Klasse 7"
- „Ich habe hier ein Foto meiner Vokabelliste aus dem Schulbuch – bitte einen Übungstest daraus machen"
- „Erstelle 10 Übersetzungssätze Latein → Deutsch für Klasse 8, Thema: a-Deklination"
- „Rechtschreibübung Deutsch Klasse 5, Fokus: Groß-/Kleinschreibung von Nomen"

---

## Hinweise

- Wenn die Lehrplan-Angabe fehlt, verwende **deutsche Lehrpläne (KMK-Rahmen)** als Standard
- Latein – unbekannte Vokabeln: Wenn in generierten Übungen (z.B. Übersetzungssätze, Grammatikaufgaben) Vokabeln vorkommen, die nicht in den verwendeten Lektionen enthalten sind, füge am Ende des Dokuments (vor dem Lösungsschlüssel) einen Abschnitt „Vokabelhilfe" ein mit einer Tabelle aller zusätzlich benötigten Wörter (Latein | Deutsch).
- Für Latein: Orientierung an gängigen Lehrwerken wie *Prima* oder *Cursus*
- Für Englisch: A2-Niveau als Orientierung für Klasse 7, B1-Niveau als Orientierung für Klasse 8–9
- Wenn hochgeladene Inhalte unklare Vokabeln enthalten, lieber nachfragen als falsche Übersetzungen generieren
- Bei Wunsch nach mehreren Aufgabentypen: Abschnitte klar trennen und nummerieren