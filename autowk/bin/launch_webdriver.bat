@echo off
setlocal
set MINI=%WEBKIT_INSPECTOR_SERVER%
set WKPORT=%WEBKIT_WEBDRIVER_PORT%
.\bin\WebDriver.exe -t %MINI% -p %WKPORT%
