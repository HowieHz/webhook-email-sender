del .\dist\webhook-email-sender.exe
pyinstaller .\src\main.py --onefile
ren .\dist\main.exe webhook-email-sender.exe
