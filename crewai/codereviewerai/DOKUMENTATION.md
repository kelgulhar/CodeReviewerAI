# CodeReviewerAI Dokumentation

CodeReviewerAI ist ein Multi-Agent-System, das automatische Code-Reviews durchführt. Es nutzt CrewAI und mehrere spezialisierte Agenten, die verschiedene Aspekte von Code analysieren.

## Was macht das System?

Das System analysiert GitHub-Repositories und erstellt Reviews zu verschiedenen Aspekten:

- Statische Code-Analyse: Findet Code-Smells, Style-Probleme und strukturelle Schwächen
- Sicherheitsanalyse: Sucht nach Sicherheitslücken und riskanten Patterns
- Architektur-Review: Bewertet Design-Qualität und Modularität
- Performance-Analyse: Identifiziert Bottlenecks und Optimierungsmöglichkeiten
- Code-Qualität: Prüft Lesbarkeit, Dokumentation und Test-Coverage

## Technologie

- CrewAI 1.9.3 als Framework
- Python 3.10-3.13
- UV als Package Manager
- OpenAI API (oder lokaler LLM)
- Custom Tools, SerperDev für Web-Suche, eigener MCP Server

---

## Wie funktioniert es?

Das System arbeitet sequenziell: Jeder Agent analysiert das Repository nacheinander und erstellt seinen eigenen Report.

```
Input (projects.json)
    ↓
Static Analyst → static_analysis.md
    ↓
Security Reviewer → security_review.md
    ↓
Architecture Analyst → architecture_review.md
    ↓
Performance Optimizer → performance_analysis.md
    ↓
Code Quality Reviewer → code_quality_review.md
```

Die Crew orchestriert die 5 Agenten, jeder hat seine spezifischen Tasks und Tools. Der MCP Server liefert zusätzliche Code-Metriken.

---

## Die Agenten

**Static Analyst**: Macht statische Code-Analyse, findet Code-Smells und Style-Probleme. Nutzt ReadProjectTool, CloneRepoTool, ReadRepoFilesTool, SerperDevTool und MCP Tools. Output: `output/static_analysis.md`

**Security Reviewer**: Sucht nach Sicherheitslücken und riskanten Patterns. Nutzt CloneRepoTool, ReadRepoFilesTool, SerperDevTool und MCP Tools. Output: `output/security_review.md`

**Architecture Analyst**: Bewertet Architektur und Design, schaut auf Modularität und Maintainability. Nutzt CloneRepoTool, ReadRepoFilesTool und MCP Tools für Dependency-Analyse. Output: `output/architecture_review.md`

**Performance Optimizer**: Findet Performance-Bottlenecks und ineffiziente Patterns. Nutzt CloneRepoTool, ReadRepoFilesTool und MCP Tools für Komplexitäts-Metriken. Output: `output/performance_analysis.md`

**Code Quality Reviewer**: Prüft Code-Qualität, Dokumentation und Test-Coverage. Nutzt CloneRepoTool, ReadRepoFilesTool und MCP Tools für Duplikation und Dokumentation. Output: `output/code_quality_review.md`

**Report Agent**: Liest die Ergebnisse der vorherigen Agenten (statische Analyse, Security, Architektur, Performance, Code-Qualität) aus dem Kontext und fasst sie zu einem gemeinsamen Abschlussbericht zusammen. Der Bericht ist nach Bereichen gegliedert (z.B. Überblick, Statische Analyse, Sicherheit, Architektur, Performance, Code-Qualität, Empfehlungen) und hebt die wichtigsten Punkte und nächsten Schritte hervor. Output: `output/final_report.md`

---

## Tasks

Die Tasks sind in `config/tasks.yaml` definiert. Jeder Agent hat einen Task, der einen Markdown-Report im `output/` Verzeichnis erstellt.

## Tools

**Custom Tools:**
- ReadProjectTool: Liest die Repository-URL aus der JSON-Konfiguration
- CloneRepoTool: Klont das Git-Repository lokal
- ReadRepoFilesTool: Liest und verkettet Source-Code-Dateien

**Externe Tools:**
- SerperDevTool: Web-Suche für Security-Informationen und Best Practices

**MCP Tools:**
Der eigene MCP Server stellt 5 Tools bereit:
- calculate_code_metrics: Berechnet Cyclomatic Complexity
- get_code_statistics: Liefert Code-Statistiken (Zeilen, Dateien, etc.)
- detect_code_duplication: Findet duplizierten Code
- analyze_dependencies: Analysiert Abhängigkeiten zwischen Modulen
- scan_security_patterns: Scannt nach bekannten Security-Patterns

Die MCP-Tools sind über `MCPServerAdapter` in `crew.py` eingebunden. Die Struktur liegt unter `mcp/code_metrics_server/`.

---

## Installation

**Voraussetzungen:**
- Python >= 3.10, < 3.14
- UV Package Manager
- Git
- OpenAI API Key (Serper.dev API Key optional)

**Installation:**
```bash
pip install uv
cd crewai/codereviewerai
crewai install
uv add crewai-tools[mcp]
```

**Konfiguration:**

Erstelle eine `.env` Datei:
```env
OPENAI_API_KEY=sk-...
SERPER_API_KEY=your_key  # optional
MODEL=gpt-4
```

Und konfiguriere `input/projects.json`:
```json
{
  "project": "https://github.com/username/repository"
}
```

## Verwendung

Einfach ausführen mit:
```bash
crewai run
```

oder

```bash
python -m codereviewerai.main
```

Die Reports werden dann im `output/` Verzeichnis gespeichert.

## Technische Details

Das System nutzt einen sequenziellen Workflow (`Process.sequential`). Die Agenten rufen Tools basierend auf ihren Task-Beschreibungen auf. Für Performance werden Repositories mit `--depth 1` geklont, und es gibt Limits: Dateien > 200KB werden übersprungen, der Gesamt-Output ist auf 200.000 Zeichen begrenzt.

Das LLM kann über die `.env` Datei konfiguriert werden (OpenAI oder lokaler LLM).

## Referenzen

- [CrewAI Dokumentation](https://docs.crewai.com)
- [CrewAI Tools](https://docs.crewai.com/en/tools/overview)
- [MCP Protocol](https://modelcontextprotocol.io)
- [Serper.dev](https://serper.dev)
