rem taskkill /PID %1 /F

call findport 80

FOR /F "tokens=5 delims= " %%P IN ('netstat -ano ^| findstr 127.0.0.1:80') DO TaskKill.exe /F /PID %%P
FOR /F "tokens=5 delims= " %%P IN ('netstat -ano ^| findstr 0.0.0.0:80') DO TaskKill.exe /F /PID %%P

call findport 80
