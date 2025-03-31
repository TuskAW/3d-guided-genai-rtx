<h2><img align="center" src="https://github.com/user-attachments/assets/cbe0d62f-c856-4e0b-b3ee-6184b7c4d96f">3D Guided Gen AI Blueprint - FLUX NIM</h2>


This Blueprint utilizes the FLUX NIM to allow users to control the output of a FLUX image generation using 3D elements in Blender. 

# Prerequisites: 

Download the [NIM Prerequisite Installer](https://assets.ngc.nvidia.com/products/api-catalog/rtx/NIM_Prerequisites_Installer_03052025.zip), extract the zip file and run the NIMSetup.exe file, and follow the instructions in the setup dialogs. This will install the necessary system components to work with NVIDIA NIMS on your system.

You will need to reboot your computer to complete the installation.

Git is required and should be installed using winget from a command prompt::
```
winget install --id Git.Git 
```

Install Microsoft Visual C++ 2015-2022 Redistributable Package  
[https://aka.ms/vs/17/release/vc\_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)
or
```
winget install Microsoft.VCRedist.2015+.x64
```

 ![image101](https://github.com/user-attachments/assets/ff2ce11a-c1b1-40dd-aae7-187f918b240e)

This blueprint requires the installation of Blender. The blueprint has been tested with the Blender 4.28 LTS (Long Term Support) build.   
[https://www.blender.org/download/release/Blender4.2/blender-4.2.7-windows-x64.msi](https://www.blender.org/download/release/Blender4.2/blender-4.2.7-windows-x64.msi)

Blender 4.28 can also be installed using winget from a command prompt:
```
winget install --id 9NW1B444LDLW |
```

| IMPORTANT NOTE | Once Blender has been installed, you must open and then close the Blender application to properly set the paths needed by the Blueprint installer. |
| :---- | :---- |

 Obtain a HuggingFace API Access Token  
Open and command prompt and type the following:  

```
set HF_TOKEN
```

If a value is shown for the HF\_TOKEN like in the image below you can skip the steps for obtaining a HugginFace API Access Token and proceed to [Installing the Blueprint](#installing-the-blueprint)  
![image102](https://github.com/user-attachments/assets/9faac397-1ed0-4bfb-a426-fa798d7af023)


If the command returns that the environment variable HF\_TOKEN is not defined, complete the steps below.  
![image103](https://github.com/user-attachments/assets/fd687cf9-0834-4b08-a37e-c4f40b89fc1c)


Create a user account at [https://huggingface.co/](https://huggingface.co/) or login to your existing account.   
Select the “Settings” option on the left-hand menu.  
![image104](https://github.com/user-attachments/assets/1c7fe06c-5482-4e89-92bc-cf2dd8a05bcf)


From the Left-Hand Menu select Access Tokens  
![image105](https://github.com/user-attachments/assets/196f11be-bf61-4f12-a695-c4ebbe750d3d)

Create a new Access Token with READ permissions. (Note: If you have an existing Access Token with read permissions you may use it instead of creating a new access token)

![image106](https://github.com/user-attachments/assets/6e5624ea-b1f9-4f7d-b47e-327eeb28fe65)

Copy your access token.


### Create a HF\_TOKEN environment variable 

Open a command prompt and issue the following command:

```
setx HF_TOKEN hf_access_token 

hf_access_token represents the access token value you created in the step above
```

Once you have generated an access token you’ll need to agree to the FluxDev Non-Commercial License Agreement and acknowledge the Acceptable Use Policy by visiting:  [https://huggingface.co/black-forest-labs/FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev)  
![image107](https://github.com/user-attachments/assets/265ba0e8-dc96-4d28-972f-255e7bfc085a)

Click the Agree and access repository button. 

# Installing the Blueprint:

Open a command prompt at the location where you would like the Blueprint files to be installed.

Download the Blueprint using Git.
```
git clone https://github.com/NVIDIA-AI-Blueprints/3d-guided-genai-rtx.git
```
Then 
```
cd 3d-guided-genai-rtx
```

From 3d-guided-genai-rtx folder, run Setup.bat (It is recommended to run this batch file from the command line)

The setup installer will install ComfyUI, the ComfyUI plugin for Blender, and other components required for the blueprint. 

Installation may fail if long path name support is not enabled on the system, the installer will prompt if long pathname support isn’t currently enabled, and will provide an option to enable it. Enabling long path support requires rebooting the system. Once the system has been rebooted, re-run Setup.bat and you will be presented with an option menu.  
![image108](https://github.com/user-attachments/assets/3f4bb20d-9d17-47d8-a00a-a417355cc391)

Choose option \#3 when resuming an installation.

Installation will take up to 20 minutes depending on download speed.  
Once complete the installation will list the ComfyUI Path, and Python Path, this information will be used to set up the Blender ComfyUI add-on.   
![image109](https://github.com/user-attachments/assets/74abeef1-c970-49de-ac82-a913118d4ee9)


# Configure Blender:

Once installation is complete start Blender and press CTRL+, to open Preferences or select from the menu Edit \>\>Preferences  
![image110](https://github.com/user-attachments/assets/f31b9939-8f40-47b6-b582-dda5a96be13e)

Select the Add-On section , and click the checkbox next to ComfyUI BlenderAI node.  
Expand the ComfyUI BlenderAI node section by clicking on the \>  
![image111](https://github.com/user-attachments/assets/d5466879-fab4-4a57-a2c1-2cca5b99be1c)

In the ComfyUI Path and the Python Path configuration section, input the paths shown at the end of the blueprint installation process. Alternatively, you can click the folder icon and navigate to the installation location and select the ComfyUI folder, and the python\_embedded folder in the ComfyUI installation. 

## Open the Blueprint Blender File

From the Blender menu select File \>\> Open  
![image112](https://github.com/user-attachments/assets/0c222a1b-f76e-4240-a265-611358bcbea7)

Navigate to Documents \>\> Blender    
Select the **Guided\_GenAI\_BP.blend** file  
![][image13]![image113](https://github.com/user-attachments/assets/f30729b4-a7f5-4b2f-8592-4a9176a723a0)

![image114](https://github.com/user-attachments/assets/2319b3a4-2be8-4e79-862e-f894d65bd698)


If necessary expand the panel in the upper left viewport by clicking on the \< indicator. Alternatively move the mouse into the upper left viewport and press the “n” key on the keyboard.

![image115](https://github.com/user-attachments/assets/dbc2a9ae-0db6-406b-a6d2-430f4972b14e)

Select the ComfyUI X Blender tab if needed. Click the **Launch/Connect to ComfyUI** button to start a local ComfyUI server instance. 

It may take up to two minutes to start the ComfyUI service and establish a connection.  
![image116](https://github.com/user-attachments/assets/bb1df709-830e-4531-a5aa-57c590e82e5d)

NOTE:  The Blender system console can be opened from the Blender Menu selection Window \>\> Toggle System Console. The system console can help provide additional information about the ComfyUI startup process and provide updates while ComfyUI tasks are running.

Once ComfyUi has started and is ready the panel will change and a **Run** button will appear.  
![image117](https://github.com/user-attachments/assets/47de07fa-7c51-4d3e-abe9-5ec5d4f5c8a0)

If the Run button does not appear or the **Launch/Connect to ComfyUI** reappears, check the system console for any error messages.

Click the Run button.

# NIM Setup

If the FLUX NIM has not been set up prior to running the workflow, the ComfyUI NIM node will open the webpage to download the NimSetup.exe. Run the NIM Setup and follow the prompts to complete the setup.   
![image118](https://github.com/user-attachments/assets/b956ae9f-2c3e-4bfb-a7bb-10a90ec717f8)

After running the NIM Setup, close and restart Blender if it’s open, in Blender open the **Guided\_GenAI\_BP.blend** file.

Click **Launch/Connect to ComfyUI** to reconnect to ComfyUI, then Click **Run.**  

The first time the FLUX NIM is utilized it will need to download models from NVIDIA NGC and setup the FLUX NIM container, this process can take up to 20 minutes or more depending on the connection speed.

# Guided GenAI Workflow

There will be an initial connection delay when first connecting to the NIM during a session which may take between 2-5 minutes. 

By default the sample workflow will use the viewport scene combined with the following prompt to generate an image that matches both the overall look of the 3D scene, and the text prompt:  
*“a stunning professional photo of a quaint village in the mountains in winter, a snow covered  fountain is visible in the center of the town square”*

##  Generating New Output

You can change the output, by changing either the text prompt, the 3D viewport information or both. NOTE:  When generating output, some parameter must be changed before it’s possible to generate a new output, either the 3D scene information, prompt, or some parameter. If nothing has been changed the workflow will not process a new image. 

The ComfyUI Connector panel is linked to the Input Text Node, you can change the prompt information here.   
![image119](https://github.com/user-attachments/assets/413031a0-4bf7-4c02-89fe-ed03c490f10f)


In the prompt input area, add some additional information to the end of the existing text to change the output, for example try any of the following:  
“At sunset”  
“At night”  
“In the rain”

### Changing the 3D Scene

With the mouse in the upper left viewport press SHIFT \+ \~ to enter navigation mode. You can fly though the scene using the WASD keys and using the mouse to point in a direction. The E and F keys raise and lower the camera. Navigate the scene to find different camera angles.

### Replace Objects

Click on the fountain object and click delete on the keyboard to remove the fountain.  
![image120](https://github.com/user-attachments/assets/cd3a850f-8662-46d4-bdcf-7de218690c17)

In the lower left area of the screen grab the boat object and drag it into the upper left viewport to the general location where the fountain was previously.   
![image121](https://github.com/user-attachments/assets/45749569-b5c9-4200-89d9-b7dbde8bb26f)

Replace the entire prompt with one of these:  
“A stunning profession photo of a modern luxury boat in the canals of Venice, classical buildings, at sunset”  
“An abandoned boat sitting between rows of warehouses”  
![image122](https://github.com/user-attachments/assets/932aef4f-06d9-467e-9a4e-89f867ccd66d)


![image123](https://github.com/user-attachments/assets/5851c084-52c1-4f25-9405-8f15db993d2d)

### Adjusting the Image Output Location
Change the output path in the Image Save node to point to a location on your system where you would like to save generated images.
![image](https://github.com/user-attachments/assets/ffac56d5-23bf-4ddd-87eb-e34bb46f821d)

# Restarting the ComfyUI Server

If errors occur when working with the NIM it may be necessary to restart the ComfyUI Server. To restart ComfyUI, place your mouse cursor in the ComfyUI node graph area and press “N” to display the panel.  
![image124](https://github.com/user-attachments/assets/48d80d38-dc45-45a9-9ed4-bdc4e2f496e9)


Click the ![image125](https://github.com/user-attachments/assets/065a8cc9-460e-48a0-abab-8a8dec9a0994) icon to stop ComfyUI.  
Click the ![image126](https://github.com/user-attachments/assets/fddc145f-ac73-4228-9639-e69be7abc8bd) icon again to restart ComfyUI, or click the **Launch/Connect to ComfyUI** button.

Re-run the workflow.



