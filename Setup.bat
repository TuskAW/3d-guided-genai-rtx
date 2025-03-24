@echo off

REM Set the base_dir variable, this will allow us to know where the original install files were launched from.
set "base_dir=%cd%"
set "comfyui_install_dir=.\ComfyUI_windows_portable\"


REM Install 7zip
REM winget install -e --id 7zip.7zip

REM Install GIT 
REM winget install -e --id Git.Git

REM if no arguments are present or we have searched all arguments without finding one we want to act on, go to the comfyui install step
IF "%~1"=="" (
    ECHO NO ARGUMENTS SUPPLIED
    GOTO CheckExistingComfyInstall
)

:ProcessArg
REM if no arguments are present or we have searched all arguments without finding one we want to act on, go to the comfyui install step
if "%~1"=="" goto :CheckExistingComfyInstall

IF /I "%1"=="-i" (
    ECHO Custom ComfyUI Path provided:
    IF EXIST "%2" (
        IF "%2:~-1%" NEQ "\" (
            set "comfyui_install_dir=%2\"
        ) ELSE (
            set "comfyui_install_dir=%2"
        )
        ECHO %comfyui_install_dir%
        SHIFT
    ) ELSE (
        ECHO "An existing directory MUST be provided when using the -i command line option. Install will exit."
        GOTO END
    )
)

IF /I "%1"=="--installFolder" (
    ECHO Custom ComfyUI Path provided:
    IF EXIST "%2" (
        IF "%2:~-1%" NEQ "\" (
            set "comfyui_install_dir=%2\"
        ) ELSE (
            set "comfyui_install_dir=%2"
        )
        ECHO %comfyui_install_dir%
        SHIFT
    ) ELSE (
        ECHO "An existing directory MUST be provided when using the -i command line option. Install will exit."
        GOTO END
    )
)
shift
GOTO ProcessArg

:SetManifest
SET manifestFile=%1
SET "customManifest=True"

:CheckExistingComfyInstall
REM Check to see if this is a default or previous user install with an existing ComfyUI installation
IF EXIST %comfyui_install_dir%comfyui (
    ECHO An existing ComfyUI installation was found at: %comfyui_install_dir%
    GOTO GetUserInput
)

REM Check to see if this is a custom location install with an existing ComfyUI installation
IF EXIST %comfyui_install_dir%ComfyUI_windows_portable\comfyui (
    SET "comfyui_install_dir=%comfyui_install_dir%ComfyUI_windows_portable\"
    ECHO An existing ComfyUI installation was found at: %comfyui_install_dir%
    GOTO GetUserInput
)

REM If no exist install is found install
GOTO StartInstall


:GetUserInput
REM Prompt the user to decide how to proceed
ECHO An existing ComfyUI installation was found in this directory. How would you like to proceed?
echo 1. Download fresh ComfyUI, overwrite existing installation, and install component files
ECHO 2. Update ComfyUI to current and install component files
ECHO 3. Only install component files  - (choose this when resuming an installation)
ECHO 4. Open existing ComfyUI without making changes
ECHO 0. Exit
    
SET /P choice="Enter your choice (1,2,3 or 4): "
ECHO Option %choice% was selected
IF "%choice%"=="1" (
	ECHO Downloading and installing ComfyUI and installing component files
	GOTO StartInstall
) ELSE IF "%choice%"=="2" (
	pushd %comfyui_install_dir%update
	ECHO Updating existing ComfyUI and installing component files
	CALL update_comfyui.bat
	popd
	GOTO InstallPythonPackages        
) ELSE IF "%choice%"=="3" (
	ECHO Installing component files only
	GOTO InstallPythonPackages
) ELSE IF "%choice%"=="4" (
	pushd %comfyui_install_dir%
	CALL run_nvidia_gpu.bat
	popd
	GOTO END
) ELSE IF "%choice%"=="0" (
	GOTO END
) ELSE (
	ECHO Invalid Selection!!!!
	ECHO Please select a valid option...
	GOTO CheckExistingComfyInstall
) 
  

:StartInstall
ECHO Download ComfyUI
curl -OL https://github.com/comfyanonymous/ComfyUI/releases/download/latest/ComfyUI_windows_portable_nvidia_or_cpu_nightly_pytorch.7z

REM I've had issues with the curl command failing, so check and bail out if it has
IF %ERRORLEVEL% NEQ 0 (
    ECHO Problem with file download, try again
    EXIT
) ELSE (
    REM Since 7z is not normally in the path, it's hard coded to the default location
    ECHO Extract ComfyUI
    IF "%comfyui_install_dir%"==".\ComfyUI_windows_portable\" (
	tar -xvf .\ComfyUI_windows_portable_nvidia_or_cpu_nightly_pytorch.7z
		
    ) ELSE (
		mkdir %comfyui_install_dir% 2>nul
		pushd %comfyui_install_dir%
		tar -xvf .\ComfyUI_windows_portable_nvidia_or_cpu_nightly_pytorch.7z
		popd
		SET "comfyui_install_dir=%comfyui_install_dir%\ComfyUI_windows_portable\
    )
	echo The current directory is: %CD%
	ren ".\ComfyUI_windows_portable_nightly_pytorch" "ComfyUI_windows_portable"
	
    GOTO InstallPythonPackages
)

	


:InstallPythonPackages
REM Get the python packages that the install script needs
ECHO Install the Python Dependencies
ECHO %comfyui_install_dir%python_embeded\python.exe -m pip install requests gitpython py7zr huggingface-hub validators elevate3
%comfyui_install_dir%python_embeded\python.exe -s -m pip install --upgrade pip
%comfyui_install_dir%python_embeded\python.exe -m pip install requests gitpython huggingface-hub validators elevate 
rem %comfyui_install_dir%python_embeded\python.exe -m pip install py7zr

REM Run the install script
ECHO Download the Rest of the content

ECHO "%comfyui_install_dir%python_embeded\python.exe" -s .\installmill.py %* --baseFolder "%base_dir%" --installFolder "%comfyui_install_dir%"
start cmd /k "%comfyui_install_dir%python_embeded\python.exe -s .\installmill.py %* --baseFolder "%base_dir%" --installFolder %comfyui_install_dir%"
rem %comfyui_install_dir%python_embeded\python.exe -s .\installmill.py %* --baseFolder %base_dir% --installFolder %comfyui_install_dir%
rem exit

:END
