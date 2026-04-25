' Golden Bullet - silent launcher.
' Resolves the project directory from this script's location, then launches
' main.py via pythonw.exe (windowless, no console flash). If the venv has
' not been created yet, shows a messagebox pointing the user at setup.ps1.

Option Explicit

Dim fso, shell, scriptDir, pythonw, mainPy
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = scriptDir & "\venv\Scripts\pythonw.exe"
mainPy = scriptDir & "\main.py"

If Not fso.FileExists(pythonw) Then
    MsgBox "Virtual environment not found." & vbCrLf & vbCrLf & _
           "Please run setup.ps1 first to install dependencies." & vbCrLf & vbCrLf & _
           "From PowerShell in this folder, run:" & vbCrLf & _
           "  powershell -ExecutionPolicy Bypass -File setup.ps1", _
           vbExclamation, "Golden Bullet"
    WScript.Quit 1
End If

shell.CurrentDirectory = scriptDir
shell.Run """" & pythonw & """ """ & mainPy & """", 0, False
