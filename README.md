

# Glosas de Guardia - Digital Garden

## Publicación en 1-Click (Manual)

Para publicar los cambios de tu vault de Obsidian en GitHub Pages en cualquier momento:
- Simplemente haz doble click en el archivo **`Publicar_Web.bat`** (o en el acceso directo en tu Escritorio: **`Publicar Glosas de Guardia`**).

---

## Automatización 100% Automática (Diaria y al Encender el PC)

Ya hemos configurado el sistema para que se ejecute **en segundo plano sin ventanas ni molestias**:
- **Al encender el ordenador**: Cada vez que enciendas el PC (a cualquier hora), Windows ejecutará la sincronización en segundo plano de forma 100% invisible.
- **Tarea programada diaria**: Se ejecuta a las 12:00 PM si el equipo permanece encendido.
- **Si quieres reconfigurar o verificar esta automatización en el futuro**:
  - Simplemente ejecuta: `uv run python configurar_tarea_diaria.py`

---

# How to run manually

- Use uv to install the dependencies: `uv sync`
- Sync & publish via Python: `uv run python publish.py`
- Or run the build manually: `uv run python build.py`

# How to set up Github pages

- Go to the settings of your repository
- Click on "Pages"
- In "Source", click "GitHub Actions"
- Then, click "Configure" in "Static HTML
- Change "path" to "public"
- Click on "Save"