' Golden Bullet - shortcut installer.
' Creates Desktop and Start Menu shortcuts pointing at run.vbs.
' Uses the standard Microsoft-documented WScript.Shell pattern.
' Run directly (double-click) or via setup.ps1.

Option Explicit

Dim fso, shell, scriptDir, runVbs, iconPath
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
runVbs = scriptDir & "\run.vbs"
iconPath = scriptDir & "\icon.ico"

If Not fso.FileExists(runVbs) Then
    MsgBox "run.vbs not found in " & scriptDir & vbCrLf & _
           "Cannot create shortcut.", vbCritical, "Golden Bullet"
    WScript.Quit 1
End If

Dim desktopPath, startMenuDir, desktopLnk, startMenuLnk
desktopPath = shell.SpecialFolders("Desktop")
startMenuDir = shell.SpecialFolders("Programs") & "\Golden Bullet"

If Not fso.FolderExists(startMenuDir) Then
    fso.CreateFolder(startMenuDir)
End If

desktopLnk = desktopPath & "\GoldenBullet.lnk"
startMenuLnk = startMenuDir & "\GoldenBullet.lnk"

Sub MakeShortcut(lnkPath)
    Dim sc
    Set sc = shell.CreateShortcut(lnkPath)
    sc.TargetPath = runVbs
    sc.WorkingDirectory = scriptDir
    sc.IconLocation = iconPath
    sc.Description = "Golden Bullet Risk Calculator"
    sc.Save
End Sub

MakeShortcut desktopLnk
MakeShortcut startMenuLnk

MsgBox "Shortcuts created:" & vbCrLf & _
       "  " & desktopLnk & vbCrLf & _
       "  " & startMenuLnk & vbCrLf & vbCrLf & _
       "Tip: launch once, then right-click the taskbar icon " & _
       "and pick 'Pin to taskbar'.", _
       vbInformation, "Golden Bullet"
