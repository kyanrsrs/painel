@echo off

cd /d "%~dp0"  # Vá para o diretório do script
python "DiscordDelete.py"  # Execute o script Python
pause  # Mantenha o CMD aberto para ver os resultados
