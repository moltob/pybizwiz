@echo off

set LOCAL=%~dp0.
set SCRIPT=update-container.sh

pushd %LOCAL%

dos2unix -n %SCRIPT% ux-%SCRIPT%

scp ux-%SCRIPT% admin@diskstation:~/scripts
ssh -t admin@diskstation ~/scripts/ux-%SCRIPT%

del /Q ux-%SCRIPT%

popd
