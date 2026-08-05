@echo off
title Publicar Glosas de Guardia
chcp 65001 > nul
cd /d "%~dp0"

echo.
echo ========================================================
echo        PUBLICAR GLOSAS DE GUARDIA EN GITHUB PAGES
echo ========================================================
echo.

uv run python publish.py

echo.
echo Presione cualquier tecla para cerrar esta ventana...
pause > nul
