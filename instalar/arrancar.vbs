' arrancar.vbs
' Inicia el servidor DoctorCure en segundo plano (sin ventana de consola).
' Se ejecuta automáticamente al iniciar sesión en Windows (Programador de tareas).

Option Explicit

Dim objShell
Set objShell = CreateObject("WScript.Shell")

' El 0 como segundo argumento oculta la ventana de la consola.
' El False final no espera a que termine (corre en background).
objShell.Run "cmd /c C:\DoctorCure\start_server.bat", 0, False

Set objShell = Nothing
