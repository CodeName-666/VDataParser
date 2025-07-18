# UI-Erstellungsablauf

Dieses Diagramm veranschaulicht die einzelnen Schritte vom Design der Oberfläche bis zur fertigen Implementierung. Jeder Knoten beschreibt kurz, was im jeweiligen Schritt passiert.

```mermaid
flowchart TD
    Design["UI-Design\n- Entwurf der Ansicht\n- Definition der Komponenten"] --> Export["Design-Export\n(JSON/XML mit\nUI-Beschreibung)"]
    Export --> Script["Python-Skript\n- liest Exportdaten\n- generiert Klassen"]
    Script --> Files["Generierte Dateien\n- Quellcode\n- Layouts"]
    Files --> Integration["Integration in die App\n- Anpassungen\n- Tests"]
    Integration --> Implementation["Implementierte UI\n- einsatzbereit"]
```

