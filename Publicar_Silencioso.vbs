Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\josua\Development\Glosas de guardia"
WshShell.Run "cmd /c uv run python publish.py", 0, False
