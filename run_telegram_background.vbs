Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "D:\tradeAutomation"
WshShell.Run "D:\tradeAutomation\.venv\Scripts\pythonw.exe telegram_listener.py", 0, False
