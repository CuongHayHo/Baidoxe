' Run command in hidden window
' Usage: cscript.exe run-hidden.vbs "command"

Set objShell = CreateObject("WScript.Shell")
strCommand = WScript.Arguments(0)
objShell.Run strCommand, 0, False
