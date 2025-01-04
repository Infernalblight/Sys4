@echo off
msg * "Your Windows drivers will be updating. Please wait..."
timeout /t 10 /nobreak > NUL  :: Wait for 10 seconds

shutdown /r /t 0  :: Restart the PC after 10 seconds
