Set WshShell = CreateObject("WScript.Shell")
Set args = WScript.Arguments

If args.Count = 0 Then
    WScript.Quit
End If

jobName = args(0)
cmd = "py D:\dark_factory\dark_scheduler.py --job " & jobName
WshShell.Run cmd, 0, False