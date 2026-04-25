@echo off
REM setup_venv.bat - Configuração para Windows

echo =========================================
echo Network Scanner - Setup com VirtualEnv
echo =========================================

REM Cria venv
echo 📦 Criando ambiente virtual...
python -m venv venv

REM Ativa venv
echo 🔄 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Atualiza pip
echo ⬆️ Atualizando pip...
python -m pip install --upgrade pip

REM Instala dependências
echo 📥 Instalando dependências...
pip install -r requirements.txt

echo.
echo 🎉 Setup concluído!
echo.
echo Para ativar o ambiente:
echo   venv\Scripts\activate.bat
echo.
echo Para executar o scanner:
echo   venv\Scripts\python main.py --method ping
echo.
pause