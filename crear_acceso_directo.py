import os
import subprocess
from pathlib import Path

def crear_acceso_directo():
    desktop_path = Path(os.path.expanduser("~/Desktop"))
    project_dir = Path(__file__).parent.resolve()
    target_bat = project_dir / "Publicar_Web.bat"
    shortcut_path = desktop_path / "Publicar Glosas de Guardia.lnk"

    print(f"Creando acceso directo en el Escritorio: {shortcut_path}")

    ps_command = f"""
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut('{shortcut_path}')
    $Shortcut.TargetPath = '{target_bat}'
    $Shortcut.WorkingDirectory = '{project_dir}'
    $Shortcut.Description = 'Publicar sitio web Glosas de Guardia en GitHub Pages'
    $Shortcut.Save()
    """

    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_command], check=True)
        print("[OK] Acceso directo creado exitosamente en el Escritorio.")
    except Exception as e:
        print(f"ERROR creando acceso directo: {e}")

if __name__ == "__main__":
    crear_acceso_directo()
