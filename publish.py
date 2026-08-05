import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Configuración de rutas
VAULT_DIR = Path(r"C:\Users\josua\OneDrive\Documents\ObsidianVault")
PROJECT_DIR = Path(__file__).parent.resolve()
CONTENT_DIR = PROJECT_DIR / "content"

import stat

def handle_remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def sync_vault():
    print(f"--- 1/3. Sincronizando notas desde Obsidian ---")
    if not VAULT_DIR.exists():
        print(f"ERROR: No se encontró el vault de Obsidian en {VAULT_DIR}")
        sys.exit(1)

    print(f"Origen: {VAULT_DIR}")
    print(f"Destino: {CONTENT_DIR}")

    # Limpiar la carpeta content para reflejar borrados en Obsidian
    if CONTENT_DIR.exists():
        for item in CONTENT_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item, onerror=handle_remove_readonly)
            else:
                try:
                    item.unlink()
                except PermissionError:
                    os.chmod(item, stat.S_IWRITE)
                    item.unlink()
    else:
        CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    copied_files = 0
    # Copiar omitiendo elementos ocultos (.obsidian, .trash, .smart-connections, etc.)
    for root, dirs, files in os.walk(VAULT_DIR):
        # Excluir directorios ocultos
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        rel_path = Path(root).relative_to(VAULT_DIR)
        dest_dir = CONTENT_DIR / rel_path
        dest_dir.mkdir(parents=True, exist_ok=True)

        for f in files:
            if f.startswith('.'):
                continue
            src_file = Path(root) / f
            dest_file = dest_dir / f
            shutil.copy2(src_file, dest_file)
            copied_files += 1

    print(f"[OK] Sincronización completada ({copied_files} archivos copiados).\n")

def run_build():
    print("--- 2/3. Generando sitio web estático (build.py) ---")
    result = subprocess.run([sys.executable, "build.py"], cwd=PROJECT_DIR)
    if result.returncode != 0:
        print("ERROR: La generación del sitio falló.")
        sys.exit(1)
    print("[OK] Build finalizado correctamente.\n")

def deploy_to_github():
    print("--- 3/3. Comprobando cambios y publicando en GitHub Pages ---")
    
    # Comprobar si hay cambios pendientes en git
    status = subprocess.run(["git", "status", "--porcelain"], cwd=PROJECT_DIR, capture_output=True, text=True)
    
    if not status.stdout.strip():
        print("[OK] No hay cambios pendientes. La web ya está actualizada.\n")
        return

    print("Cambios detectados. Añadiendo a Git...")
    subprocess.run(["git", "add", "."], cwd=PROJECT_DIR, check=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"Actualización de contenido ({timestamp})"
    print(f"Creando commit: '{commit_msg}'...")
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_DIR, check=True)

    print("Subiendo a GitHub Pages (origin main)...")
    push_result = subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT_DIR)
    
    if push_result.returncode == 0:
        print("\n=======================================================")
        print(" ¡Éxito! El contenido ha sido publicado en GitHub.")
        print(" GitHub Pages desplegará los cambios en 1-2 minutos.")
        print("=======================================================\n")
    else:
        print("ERROR: Falló el comando git push.")
        sys.exit(1)

def main():
    start_time = datetime.now()
    print("=======================================================")
    print("      PUBLICADOR DE GLOSAS DE GUARDIA")
    print("=======================================================\n")
    
    sync_vault()
    run_build()
    deploy_to_github()

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"Proceso finalizado en {elapsed:.2f} segundos.")

if __name__ == "__main__":
    main()
