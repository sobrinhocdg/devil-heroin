@echo off
chcp 65001 >nul
title AfterRelease33 Installer
echo =========================================
echo AfterRelease33 - Release v33
echo =========================================
setlocal

set PYTHON=python
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
  set PYTHON=py
  %PYTHON% --version >nul 2>&1
  if errorlevel 1 (
    echo Python 3 nao foi encontrado.
    echo Instale o Python 3 e marque a opcao "Add Python to PATH".
    pause
    exit /b 1
  )
)

echo Usando %PYTHON%...
echo Instalando dependencias...
%PYTHON% -m pip install --upgrade pip
if errorlevel 1 (
  echo Falha ao atualizar pip. Tentando continuar...
)
%PYTHON% -m pip install -r requirements.txt
if errorlevel 1 (
  echo Erro ao instalar dependencias.
  pause
  exit /b 1
)

if not exist releases (
  mkdir releases
)
echo Iniciando o servidor web...
start "" "%PYTHON%" web_server.py
timeout /t 2 >nul
start "" "http://127.0.0.1:5000"

echo Feito! O navegador deve abrir em breve.
echo Caso nao abra, acesse: http://127.0.0.1:5000
pause
