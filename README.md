

# Glosas de Guardia - Digital Garden

## Publicación en 1-Click (Recomendado)

Para publicar los cambios de tu vault de Obsidian en GitHub Pages:
- Simplemente haz doble click en el archivo **`Publicar_Web.bat`** (o en el acceso directo en tu Escritorio: **`Publicar Glosas de Guardia`**).

Este script realiza automáticamente:
1. La **sincronización** del contenido desde tu vault (`C:\Users\josua\OneDrive\Documents\ObsidianVault`) hacia `content/` (reflejando borrados y des-publicaciones).
2. La **compilación** del sitio web (`build.py`).
3. El **commit y push** a GitHub, lo que activa el despliegue automático de GitHub Pages.

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