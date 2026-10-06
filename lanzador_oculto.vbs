Set WshShell = CreateObject("WScript.Shell")
rutaActual = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
WshShell.Run chr(34) & rutaActual & "iniciar_azmuth.bat" & chr(34), 0
Set WshShell = Nothing