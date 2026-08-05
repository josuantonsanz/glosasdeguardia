import os
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.resolve()
VBS_PATH = PROJECT_DIR / "Publicar_Silencioso.vbs"
TASK_NAME = "GlosasDeGuardia_PublicarDiario"

def configurar_automatizacion_diaria():
    print("=======================================================")
    print(" CONFIGURANDO AUTOMATIZACIÓN DIARIA (100% SEGUNDO PLANO)")
    print("=======================================================\n")

    # 1. Crear Tarea Programada Diaria en Windows (schtasks)
    print("1. Creando Tarea Programada diaria (12:00 PM)...")
    cmd_schtasks = [
        "schtasks", "/Create",
        "/SC", "DAILY",
        "/TN", TASK_NAME,
        "/TR", f'wscript.exe "{VBS_PATH}"',
        "/ST", "12:00",
        "/F"
    ]
    
    res1 = subprocess.run(cmd_schtasks, capture_output=True, text=True)
    if res1.returncode == 0:
        print("[OK] Tarea programada diaria creada con éxito en Windows Task Scheduler.")
    else:
        print(f"[Aviso] No se pudo registrar la tarea programada: {res1.stderr.strip()}")

    # 2. Crear acceso directo en la carpeta de Inicio de Windows (shell:startup)
    print("\n2. Configurando ejecución automática al encender el PC (Carpeta Inicio)...")
    startup_dir = Path(os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"))
    shortcut_path = startup_dir / "Publicar_Glosas_Silencioso.lnk"

    ps_command = f"""
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut('{shortcut_path}')
    $Shortcut.TargetPath = 'wscript.exe'
    $Shortcut.Arguments = '"{VBS_PATH}"'
    $Shortcut.WorkingDirectory = '{PROJECT_DIR}'
    $Shortcut.Description = 'Publicación automática silenciosa de Glosas de Guardia'
    $Shortcut.Save()
    """

    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_command], check=True)
        print("[OK] Acceso directo silencioso creado en la carpeta de Inicio de Windows.")
        print(f"     Ruta: {shortcut_path}")
    except Exception as e:
        print(f"[Aviso] Error configurando carpeta de Inicio: {e}")

    print("\n=======================================================")
    print(" ¡AUTOMATIZACIÓN CONFIGURADA!")
    print(" - Al encender tu ordenador (a cualquier hora), la web se actualizará automáticamente en segundo plano.")
    print(" - Además, se ejecutará todos los días a las 12:00 PM si el equipo está encendido.")
    print(" - Es 100% invisible y no interrumpe tu trabajo.")
    print("=======================================================\n")

if __name__ == "__main__":
    configurar_automatizacion_diaria()
