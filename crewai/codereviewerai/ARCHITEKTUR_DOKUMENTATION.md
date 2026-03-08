# CodeReviewerAI - Architektur-Dokumentation

## 📋 Inhaltsverzeichnis

1. [Projektübersicht](#projektübersicht)
2. [Aktuelle Struktur-Analyse](#aktuelle-struktur-analyse)
3. [Empfohlene Agenten-Architektur (5 Agenten)](#empfohlene-agenten-architektur)
4. [Tool-Strategie](#tool-strategie)
5. [MCP Server Konzept](#mcp-server-konzept)
6. [Implementierungsplan](#implementierungsplan)
7. [Workflow-Diagramm](#workflow-diagramm)

---

## 🎯 Projektübersicht

**CodeReviewerAI** ist ein Multi-Agent-System basierend auf CrewAI, das automatisiert Code-Reviews durchführt. Das System analysiert GitHub-Repositories und erstellt umfassende Review-Berichte zu verschiedenen Aspekten der Code-Qualität.

### Hauptfunktionen

- **Statische Code-Analyse**: Identifizierung von Code-Smells, Style-Verletzungen und strukturellen Problemen
- **Sicherheitsanalyse**: Erkennung von Sicherheitslücken und riskanten Coding-Praktiken
- **Architektur-Review**: Bewertung der Code-Architektur und Design-Qualität
- **Performance-Analyse**: Identifizierung von Performance-Bottlenecks
- **Code-Qualität & Dokumentation**: Bewertung von Lesbarkeit, Wartbarkeit und Dokumentation

---

## 📊 Aktuelle Struktur-Analyse

### Vorhandene Komponenten

#### Agenten (definiert in `agents.yaml`)
Das System hat aktuell **6 Agenten** definiert, aber nur **1 Agent aktiv**:

| Agent | Status | Beschreibung |
|-------|--------|--------------|
| `static_analyst` | ✅ Aktiv | Führt statische Code-Analyse durch |
| `security_reviewer` | ⚠️ Inaktiv | Analysiert Sicherheitsaspekte |
| `architecture_design_analyst` | ⚠️ Inaktiv | Bewertet Architektur und Design |
| `performance_optimizer` | ⚠️ Inaktiv | Analysiert Performance-Probleme |
| `code_quality_documentation_agent` | ⚠️ Inaktiv | Bewertet Code-Qualität und Dokumentation |
| `test_coverage_agent` | ⚠️ Inaktiv | Analysiert Test-Abdeckung |

#### Tools

**Custom Tools:**
- ✅ `ReadProjectTool`: Liest Repository-URLs aus JSON-Dateien
- ✅ `CloneRepoTool`: Klont Git-Repositories in temporäre Verzeichnisse
- ✅ `ReadRepoFilesTool`: Liest und konkatiniert Source-Dateien aus Repositories

**Externe Tools:**
- ✅ `SerperDevTool`: Web-Suche für zusätzliche Kontextinformationen

#### Tasks

- ✅ `static_analysis_task`: Einzige aktive Task
- ⚠️ 5 weitere Tasks sind auskommentiert

### Identifizierte Probleme

1. **Unvollständige Implementierung**: Nur 1 von 6 Agenten ist aktiv
2. **Fehlende MCP-Integration**: Kein MCP-Server implementiert
3. **Unvollständige Tool-Nutzung**: Tools sind nur einem Agenten zugewiesen
4. **Sequentieller Workflow**: Alle Analysen könnten parallelisiert werden

---

## 🤖 Empfohlene Agenten-Architektur (5 Agenten)

### Strategische Überlegungen

Für ein optimales Code-Review-System sollten die 5 Agenten folgende Kriterien erfüllen:

1. **Klar abgegrenzte Verantwortlichkeiten**: Jeder Agent hat einen spezifischen Fokus
2. **Parallele Ausführbarkeit**: Agenten können unabhängig voneinander arbeiten
3. **Synergien nutzen**: Agenten können auf gemeinsame Tools zugreifen
4. **Vollständige Abdeckung**: Alle wichtigen Aspekte des Code-Reviews werden abgedeckt

### Empfohlene 5-Agenten-Struktur

#### Option 1: Fokus auf Kern-Aspekte (EMPFOHLEN)

| # | Agent | Verantwortlichkeit | Tools | Output |
|---|-------|-------------------|-------|--------|
| 1 | **Static Code Analyst** | Statische Analyse, Code-Smells, Style | ReadProjectTool, CloneRepoTool, ReadRepoFilesTool, CodeMetricsTool (MCP) | `static_analysis.md` |
| 2 | **Security Reviewer** | Sicherheitslücken, Vulnerabilities, Best Practices | CloneRepoTool, ReadRepoFilesTool, SecurityPatternsTool (MCP), SerperDevTool | `security_review.md` |
| 3 | **Architecture Analyst** | Architektur, Design-Patterns, Modularität | CloneRepoTool, ReadRepoFilesTool, ArchitecturePatternsTool (MCP) | `architecture_review.md` |
| 4 | **Performance Analyst** | Performance-Bottlenecks, Optimierungen | CloneRepoTool, ReadRepoFilesTool, PerformanceMetricsTool (MCP) | `performance_analysis.md` |
| 5 | **Quality & Documentation Reviewer** | Code-Qualität, Dokumentation, Test-Coverage | CloneRepoTool, ReadRepoFilesTool, DocumentationAnalyzerTool (MCP) | `quality_review.md` |

**Vorteile:**
- ✅ Klare Trennung der Verantwortlichkeiten
- ✅ Alle Agenten können parallel arbeiten
- ✅ Jeder Agent hat spezialisierte Tools
- ✅ Vollständige Abdeckung aller Review-Aspekte

**Nachteile:**
- ⚠️ Test-Coverage wird in Agent 5 integriert (weniger Fokus)

#### Option 2: Separate Test-Coverage

| # | Agent | Verantwortlichkeit |
|---|-------|-------------------|
| 1 | Static Code Analyst | Statische Analyse |
| 2 | Security Reviewer | Sicherheitsanalyse |
| 3 | Architecture Analyst | Architektur-Review |
| 4 | Performance Analyst | Performance-Analyse |
| 5 | Test Coverage Analyst | Test-Abdeckung und Test-Qualität |

**Vorteile:**
- ✅ Test-Coverage bekommt eigenen Fokus
- ✅ Sehr spezialisierte Agenten

**Nachteile:**
- ⚠️ Code-Qualität und Dokumentation werden weniger fokussiert
- ⚠️ Potenzielle Überschneidungen mit anderen Agenten

#### Option 3: Konsolidierte Struktur

| # | Agent | Verantwortlichkeit |
|---|-------|-------------------|
| 1 | Static Code Analyst | Statische Analyse + Code-Smells |
| 2 | Security & Performance Analyst | Sicherheit + Performance (kombiniert) |
| 3 | Architecture & Design Analyst | Architektur + Design-Patterns |
| 4 | Quality & Documentation Reviewer | Code-Qualität + Dokumentation |
| 5 | Test & Coverage Analyst | Tests + Coverage |

**Vorteile:**
- ✅ Weniger Agenten, aber breitere Abdeckung
- ✅ Gute Balance zwischen Spezialisierung und Effizienz

**Nachteile:**
- ⚠️ Security und Performance sind sehr unterschiedliche Domänen
- ⚠️ Potenzielle Überlastung einzelner Agenten

### 🏆 Finale Empfehlung: Option 1

**Begründung:**

1. **Klarheit**: Jeder Agent hat einen klar definierten, fokussierten Bereich
2. **Parallele Ausführung**: Alle 5 Agenten können gleichzeitig arbeiten, da sie unabhängig sind
3. **Skalierbarkeit**: Einfach erweiterbar durch zusätzliche Tools
4. **MCP-Integration**: Jeder Agent kann spezialisierte MCP-Tools nutzen
5. **Vollständigkeit**: Alle wichtigen Aspekte werden abgedeckt

**Anpassung:** Test-Coverage wird als Teil der Code-Qualität betrachtet und in Agent 5 integriert. Dies ist sinnvoll, da Test-Coverage eng mit Code-Qualität zusammenhängt.

---

## 🛠️ Tool-Strategie

### Aktuelle Tools

#### Custom Tools (bereits implementiert)

1. **ReadProjectTool**
   - **Zweck**: Liest Repository-URLs aus JSON-Konfigurationsdateien
   - **Input**: Pfad zur `projects.json`
   - **Output**: Repository-URL
   - **Verwendung**: Alle Agenten benötigen dies als Einstiegspunkt

2. **CloneRepoTool**
   - **Zweck**: Klont Git-Repositories in temporäre Verzeichnisse
   - **Input**: Repository-URL
   - **Output**: Lokaler Pfad zum geklonten Repository
   - **Verwendung**: Alle Agenten benötigen Zugriff auf den Code

3. **ReadRepoFilesTool**
   - **Zweck**: Liest Source-Dateien aus einem Repository
   - **Input**: Lokaler Repository-Pfad
   - **Output**: Konkatenierter Code-Text (max. 200KB)
   - **Verwendung**: Alle Agenten analysieren den Code

#### Externe Tools (bereits integriert)

1. **SerperDevTool**
   - **Zweck**: Web-Suche für zusätzliche Kontextinformationen
   - **Verwendung**: Besonders nützlich für Security- und Best-Practices-Recherche

### Empfohlene Erweiterungen

#### Neue Custom Tools

1. **CodeMetricsCalculatorTool**
   - **Zweck**: Berechnet Code-Metriken (Cyclomatic Complexity, Lines of Code, etc.)
   - **Input**: Repository-Pfad
   - **Output**: JSON mit Metriken
   - **Verwendung**: Static Code Analyst, Performance Analyst

2. **DependencyAnalyzerTool**
   - **Zweck**: Analysiert Abhängigkeiten zwischen Modulen
   - **Input**: Repository-Pfad
   - **Output**: Dependency-Graph
   - **Verwendung**: Architecture Analyst

3. **TestFileFinderTool**
   - **Zweck**: Identifiziert Test-Dateien und deren Coverage
   - **Input**: Repository-Pfad
   - **Output**: Liste der Test-Dateien mit Coverage-Informationen
   - **Verwendung**: Quality & Documentation Reviewer

#### MCP-Tools (siehe MCP Server Abschnitt)

Die MCP-Tools werden über den eigenen MCP-Server bereitgestellt.

---

## 🔌 MCP Server Konzept

### Was ist MCP?

**Model Context Protocol (MCP)** ist ein Standard-Protokoll, das es AI-Agenten ermöglicht, mit externen Tools, Services und Datenquellen zu interagieren. MCP-Server stellen Tools über eine standardisierte Schnittstelle bereit.

### Warum ein eigener MCP-Server?

1. **Spezialisierung**: Code-spezifische Tools, die nicht in Standard-Bibliotheken verfügbar sind
2. **Performance**: Lokale Tools können schneller sein als API-Calls
3. **Kontrolle**: Vollständige Kontrolle über die Implementierung
4. **Erweiterbarkeit**: Einfach neue Tools hinzufügen
5. **Datenbank-Integration**: Zugriff auf Best-Practices-Datenbanken

### Empfohlener MCP-Server: CodeAnalysisMCP

#### Architektur

```
CodeAnalysisMCP/
├── server.py              # MCP-Server Hauptdatei
├── tools/
│   ├── code_metrics.py    # Code-Metriken berechnen
│   ├── pattern_detector.py # Design-Patterns erkennen
│   ├── security_scanner.py # Sicherheits-Patterns scannen
│   ├── best_practices.py  # Best-Practices-Datenbank abfragen
│   └── code_snippets.py   # Code-Snippets aus Bibliothek abrufen
└── data/
    ├── best_practices.db  # SQLite-Datenbank mit Best Practices
    └── code_patterns.json # JSON mit bekannten Code-Patterns
```

#### MCP-Tools

1. **calculate_code_metrics**
   - **Zweck**: Berechnet Code-Metriken (Cyclomatic Complexity, Maintainability Index, etc.)
   - **Input**: Code-Datei oder Repository-Pfad
   - **Output**: JSON mit Metriken
   - **Verwendung**: Static Code Analyst, Performance Analyst

2. **detect_design_patterns**
   - **Zweck**: Erkennt bekannte Design-Patterns im Code
   - **Input**: Code-Datei
   - **Output**: Liste der erkannten Patterns
   - **Verwendung**: Architecture Analyst

3. **scan_security_patterns**
   - **Zweck**: Scannt Code nach bekannten Sicherheits-Patterns (SQL Injection, XSS, etc.)
   - **Input**: Code-Datei
   - **Output**: Liste der gefundenen Security-Issues
   - **Verwendung**: Security Reviewer

4. **query_best_practices**
   - **Zweck**: Fragt Best-Practices-Datenbank für spezifische Sprachen/Frameworks ab
   - **Input**: Sprache, Framework, Kategorie
   - **Output**: Best-Practices-Empfehlungen
   - **Verwendung**: Alle Agenten

5. **get_code_snippets**
   - **Zweck**: Ruft Code-Snippets aus einer Bibliothek ab (z.B. für Vergleich)
   - **Input**: Pattern-Name, Sprache
   - **Output**: Code-Snippet
   - **Verwendung**: Quality & Documentation Reviewer

#### Implementierungsdetails

**Technologie-Stack:**
- Python 3.11+
- `mcp` Python-Package
- SQLite für Best-Practices-Datenbank
- AST (Abstract Syntax Tree) für Code-Analyse

**Vorteile:**
- ✅ Wiederverwendbare Tools für alle Agenten
- ✅ Zentrale Datenbank für Best Practices
- ✅ Erweiterbar durch neue Tools
- ✅ Standardisiertes Interface (MCP)

**Alternative Ansätze:**

1. **Externe APIs nutzen**: Schneller, aber weniger Kontrolle
2. **Direkte Tool-Integration**: Einfacher, aber weniger flexibel
3. **Hybrid-Ansatz**: MCP für komplexe Tools, direkte Tools für einfache Operationen

---

## 📋 Implementierungsplan

### Phase 1: Agenten-Aktivierung (Priorität: HOCH)

**Ziel**: Alle 5 Agenten aktivieren und konfigurieren

**Schritte:**

1. **Agenten in `crew.py` aktivieren**
   ```python
   @agent
   def static_analyst(self) -> Agent:
       return Agent(
           config=self.agents_config['static_analyst'],
           llm=self.local_llm,
           tools=[ReadProjectTool(), CloneRepoTool(), ReadRepoFilesTool()],
           verbose=True
       )
   
   @agent
   def security_reviewer(self) -> Agent:
       return Agent(
           config=self.agents_config['security_reviewer'],
           llm=self.local_llm,
           tools=[CloneRepoTool(), ReadRepoFilesTool(), SerperDevTool()],
           verbose=True
       )
   
   # ... weitere Agenten
   ```

2. **Tasks in `tasks.yaml` aktivieren**
   - Alle auskommentierten Tasks aktivieren
   - PLACEHOLDER durch `{path}` ersetzen

3. **Tasks in `crew.py` registrieren**
   ```python
   @task
   def security_review_task(self) -> Task:
       return Task(
           config=self.tasks_config['security_review_task'],
           output_file='output/security_review.md',
       )
   # ... weitere Tasks
   ```

4. **Workflow anpassen**
   - Von `Process.sequential` zu `Process.sequential` (erstmal sequentiell)
   - Später auf parallele Ausführung umstellen

**Zeitaufwand**: 2-3 Stunden

### Phase 2: Custom Tools erweitern (Priorität: MITTEL)

**Ziel**: Zusätzliche Custom Tools implementieren

**Schritte:**

1. **CodeMetricsCalculatorTool erstellen**
   - Verwendet `radon` oder `pylint` für Metriken
   - Input: Repository-Pfad
   - Output: JSON mit Metriken

2. **DependencyAnalyzerTool erstellen**
   - Analysiert Import-Statements
   - Erstellt Dependency-Graph
   - Input: Repository-Pfad
   - Output: Dependency-Informationen

3. **TestFileFinderTool erstellen**
   - Findet Test-Dateien (test_*.py, *_test.py, etc.)
   - Analysiert Test-Struktur
   - Input: Repository-Pfad
   - Output: Test-Informationen

**Zeitaufwand**: 4-6 Stunden

### Phase 3: MCP-Server implementieren (Priorität: HOCH)

**Ziel**: Eigenen MCP-Server für Code-Analyse-Tools erstellen

**Schritte:**

1. **MCP-Server-Struktur erstellen**
   ```
   src/codereviewerai/mcp/
   ├── __init__.py
   ├── server.py
   ├── tools/
   │   ├── __init__.py
   │   ├── code_metrics.py
   │   ├── pattern_detector.py
   │   ├── security_scanner.py
   │   ├── best_practices.py
   │   └── code_snippets.py
   └── data/
       ├── best_practices.db
       └── code_patterns.json
   ```

2. **MCP-Server implementieren**
   - `server.py` mit MCP-Server-Logik
   - Tools als MCP-Tools registrieren
   - Datenbank initialisieren

3. **MCP-Tools implementieren**
   - `calculate_code_metrics`: Verwendet AST-Analyse
   - `detect_design_patterns`: Pattern-Matching im Code
   - `scan_security_patterns`: Regex-basierte Security-Scans
   - `query_best_practices`: SQLite-Abfragen
   - `get_code_snippets`: JSON-Datei lesen

4. **MCP-Server in CrewAI integrieren**
   ```python
   from crewai_tools import MCPServerAdapter
   from mcp import StdioServerParameters
   from codereviewerai.mcp.server import get_mcp_tools
   
   mcp_tools = get_mcp_tools()
   ```

5. **Tools zu Agenten hinzufügen**
   - Jeder Agent bekommt relevante MCP-Tools

**Zeitaufwand**: 8-12 Stunden

### Phase 4: Workflow-Optimierung (Priorität: NIEDRIG)

**Ziel**: Workflow für parallele Ausführung optimieren

**Schritte:**

1. **Task-Dependencies analysieren**
   - Welche Tasks können parallel laufen?
   - Welche Tasks benötigen Ergebnisse anderer Tasks?

2. **Parallele Ausführung implementieren**
   - `Process.sequential` beibehalten für Abhängigkeiten
   - Oder `Process.hierarchical` für komplexere Workflows

3. **Output-Konsolidierung**
   - Finaler Report-Agent, der alle Ergebnisse zusammenführt
   - Optional: Zusammenfassungs-Task

**Zeitaufwand**: 2-4 Stunden

### Phase 5: Testing & Dokumentation (Priorität: MITTEL)

**Ziel**: System testen und dokumentieren

**Schritte:**

1. **Unit-Tests für Tools**
2. **Integration-Tests für Agenten**
3. **End-to-End-Tests**
4. **Dokumentation aktualisieren**

**Zeitaufwand**: 4-6 Stunden

---

## 🔄 Workflow-Diagramm

### Aktueller Workflow (Sequentiell)

```
Input (projects.json)
    ↓
[Static Analyst]
    ├─ ReadProjectTool
    ├─ CloneRepoTool
    ├─ ReadRepoFilesTool
    └─ SerperDevTool
    ↓
Output: static_analysis.md
```

### Empfohlener Workflow (Parallele Ausführung)

```
Input (projects.json)
    ↓
    ├─→ [Static Code Analyst]
    │   ├─ ReadProjectTool
    │   ├─ CloneRepoTool
    │   ├─ ReadRepoFilesTool
    │   ├─ CodeMetricsTool (MCP)
    │   └─ BestPracticesTool (MCP)
    │   → Output: static_analysis.md
    │
    ├─→ [Security Reviewer]
    │   ├─ CloneRepoTool
    │   ├─ ReadRepoFilesTool
    │   ├─ SecurityScannerTool (MCP)
    │   └─ SerperDevTool
    │   → Output: security_review.md
    │
    ├─→ [Architecture Analyst]
    │   ├─ CloneRepoTool
    │   ├─ ReadRepoFilesTool
    │   ├─ DependencyAnalyzerTool
    │   └─ PatternDetectorTool (MCP)
    │   → Output: architecture_review.md
    │
    ├─→ [Performance Analyst]
    │   ├─ CloneRepoTool
    │   ├─ ReadRepoFilesTool
    │   ├─ CodeMetricsTool (MCP)
    │   └─ PerformanceMetricsTool (MCP)
    │   → Output: performance_analysis.md
    │
    └─→ [Quality & Documentation Reviewer]
        ├─ CloneRepoTool
        ├─ ReadRepoFilesTool
        ├─ TestFileFinderTool
        └─ DocumentationAnalyzerTool (MCP)
        → Output: quality_review.md
```

### Optional: Finaler Konsolidierungs-Agent

```
[Alle 5 Outputs]
    ↓
[Report Consolidator] (Optional)
    └─ Zusammenfassung aller Reviews
    → Output: final_review_report.md
```

---

## 🎯 Zusammenfassung der Empfehlungen

### Agenten-Architektur

✅ **5 Agenten verwenden:**
1. Static Code Analyst
2. Security Reviewer
3. Architecture Analyst
4. Performance Analyst
5. Quality & Documentation Reviewer (inkl. Test-Coverage)

### Tools

✅ **Custom Tools:**
- ReadProjectTool (bereits vorhanden)
- CloneRepoTool (bereits vorhanden)
- ReadRepoFilesTool (bereits vorhanden)
- CodeMetricsCalculatorTool (neu)
- DependencyAnalyzerTool (neu)
- TestFileFinderTool (neu)

✅ **Externe Tools:**
- SerperDevTool (bereits vorhanden)

✅ **MCP-Tools:**
- calculate_code_metrics
- detect_design_patterns
- scan_security_patterns
- query_best_practices
- get_code_snippets

### MCP-Server

✅ **Eigener MCP-Server:** CodeAnalysisMCP
- Zentrale Code-Analyse-Tools
- Best-Practices-Datenbank
- Pattern-Detection
- Security-Scanning

### Workflow

✅ **Parallele Ausführung:** Alle 5 Agenten arbeiten parallel
✅ **Output-Dateien:** Jeder Agent erstellt eigenen Report
✅ **Optional:** Finaler Konsolidierungs-Agent für Zusammenfassung

---

## 📚 Weitere Überlegungen

### Alternative Ansätze

1. **Hierarchischer Workflow**
   - Manager-Agent koordiniert andere Agenten
   - Vorteil: Bessere Koordination
   - Nachteil: Komplexer

2. **Dynamische Agent-Auswahl**
   - System wählt relevante Agenten basierend auf Code-Typ
   - Vorteil: Effizienter
   - Nachteil: Komplexer zu implementieren

3. **Iterative Reviews**
   - Agenten können aufeinander aufbauen
   - Vorteil: Tiefere Analysen
   - Nachteil: Längere Ausführungszeit

### Skalierungs-Überlegungen

- **Große Repositories**: Code-Chunking für große Projekte
- **Mehrere Repositories**: Batch-Processing
- **Caching**: Ergebnisse zwischenspeichern
- **Inkrementelle Reviews**: Nur geänderte Dateien analysieren

### Sicherheits-Überlegungen

- **Sandboxing**: Geklonte Repositories in isolierten Umgebungen
- **API-Keys**: Sicher speichern in `.env`
- **Code-Scanning**: Vorsicht bei der Ausführung von fremdem Code

---

## 🚀 Nächste Schritte

1. ✅ **Diese Dokumentation durchgehen**
2. ✅ **Agenten-Architektur finalisieren** (Option 1 empfohlen)
3. ✅ **Phase 1 starten**: Agenten aktivieren
4. ✅ **Phase 3 starten**: MCP-Server implementieren
5. ✅ **Phase 2 parallel**: Custom Tools erweitern
6. ✅ **Testing**: System testen
7. ✅ **Dokumentation**: Finale Dokumentation erstellen

---

**Erstellt am**: 2025-01-27  
**Version**: 1.0  
**Autor**: AI Assistant (basierend auf CodeReviewerAI Projekt-Analyse)
