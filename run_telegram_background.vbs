Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "D:\tradeAutomation"
WshShell.Run """D:\tradeAutomation\.venv\Scripts\pythonw.exe"" ""D:\tradeAutomation\telegram_listener.py""", 0, False

