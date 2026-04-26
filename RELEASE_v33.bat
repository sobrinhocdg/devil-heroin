@echo off
chcp 65001 >nul
title AfterRelease33 Installer v33
echo =========================================
echo AfterRelease33 - Release v33
echo Dungeon Synth MIDI Generator
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
%PYTHON% -m pip install --upgrade pip --quiet
if errorlevel 1 (
  echo Falha ao atualizar pip. Tentando continuar...
)
%PYTHON% -m pip install -r requirements.txt --quiet
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
timeout /t 3 >nul
start "" "http://127.0.0.1:5000"

echo =========================================
echo AfterRelease33 v33 instalado com sucesso!
echo =========================================
echo Servidor web iniciado.
echo Abra o navegador em: http://127.0.0.1:5000
echo Para gerar MIDI, use o formulario na pagina.
echo Arquivos serao salvos em: releases\
echo =========================================
pause
