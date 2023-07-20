@echo OFF

xcopy "dist\functions\*.js" "deploy\" /I

tar -a -c -f functions.zip deploy