import io, os, csv, requests, zipfile, subprocess, sys
# import py7zr
import shutil, argparse, urllib, validators, re, winreg, ctypes, typing
import traceback
import msvcrt
from sys import version_info
from git import Repo
from pathlib import Path
from huggingface_hub import hf_hub_download
from huggingface_hub import snapshot_download
from huggingface_hub.utils import are_progress_bars_disabled, disable_progress_bars, enable_progress_bars
from huggingface_hub import whoami
from elevate import elevate
        
def is_admin():
    try:
        # Check if the current user has administrator privileges
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False  
        

class ManifestItem:
    def __init__(self, url, location, overwrite, basefolder):
        self.url = url
        self.location = location
        self.overwrite = overwrite
        self.basefolder = basefolder
        self.valid_url = validators.url(url)
        
        #Get the overwrite value and convert it to an actual boolean
        if self.overwrite.lower() == 'true':
            self.overwrite = True
        else:
            self.overwrite = False
            
        # If the supplied URL is a valid URL
        if self.valid_url:
            self.url_parts = urllib.parse.urlsplit(url)
        else:
            self.url_parts = None

        self.item_type = self.interrogate_url()

    def interrogate_url(self):

        if not self.valid_url:
            #IF the file has an absolute path provided check if it exists
            if os.path.isabs(self.url):
                if os.path.isfile(self.url):
                    return 'LOCAL_FILE'
            else:  #IF the file path is relative, check if it exists in the install location or in the original base location.
                if os.path.isfile(self.url):
                    return 'LOCAL_FILE'
                elif os.path.isfile(os.path.normpath(os.path.join(self.basefolder,self.url))):
                    self.url=os.path.join(self.basefolder,self.url)
                    return 'LOCAL_FILE'

            if self.location.lower() == 'comfy_manager_install':
                return 'CM_MANAGER_INSTALL'
            return 'INVALID_URL'

        if self.url_parts.netloc == "huggingface.co":
            path = self.url_parts.path
            path_parts = path.split('/')
            self.repo_id = path_parts[1] + '/' + path_parts[2] if len(path_parts) > 2 else None
            element_f = path.split(self.repo_id)[1].split('/')[-1] if self.repo_id else None
            local_path, local_filename = split_tup = os.path.split(self.location)
            self.local_path = local_path
            self.local_filename = local_filename

            if element_f and len(element_f) > 0:
                self.is_file = True
                self.is_repo = False
                self.filename = element_f
                return 'HF_FILE'
            else:
                self.is_file = False
                self.is_repo = True
                self.filename = None
                return 'HF_REPO'

        elif "github.com" in self.url_parts.netloc:
            path = self.url_parts.path
            # This will return a tuple of root and extension
            split_tup = os.path.splitext(path)
            # Extract the file name and extension
            element_f = split_tup[0]
            element_x = split_tup[1]

            if element_x == '.git':
                self.is_file = False
                self.is_repo = True
                self.filename = None
                self.repo_id = os.path.basename(element_f)
                return 'GH_REPO'
            else:
                self.is_file = True
                self.is_repo = False
                self.filename = os.path.basename(element_f)
                self.repo_id = os.path.basename(element_f)
                return 'GH_FILE'
        else:
            self.is_file = True
            self.is_repo = False
            self.filename = None
            return 'UNDEFINED'



def is_package_installed(package_name):
    """Check if the Python package is installed."""
    try:
        subprocess.check_call([f'pip show {package_name}'], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def clone_or_update_repo(repo_url, local_path):
    """Clone the repo if it doesn't exist, or update it if it does."""
    if not os.path.exists(local_path):
        # Clone the repository
        print(f"Cloning repository from {repo_url} to {local_path}")
        repo = Repo.clone_from(repo_url, local_path)
    else:
        # Update the repository
        print(f"Repository already exists at {local_path}. Pulling latest changes.")
        repo = Repo(local_path)
        origin = repo.remotes.origin
        origin.pull()

def install_package_from_local_path(local_path):
    """Install the package from the local repository."""
    print(f"Installing package from {local_path}")
    subprocess.check_call([f'pip install {local_path}'], shell=True)

def manage_package(package_name, repo_url, local_path):
    """Check if the package is installed, clone/update the repo, and install the package."""
    if is_package_installed(package_name):
        print(f"{package_name} is already installed. Updating the package.")
        clone_or_update_repo(repo_url, local_path)
        
    else:
        print(f"{package_name} is not installed. Cloning the repository and installing the package.")
        clone_or_update_repo(repo_url, local_path)
       
        
# Function to Clone github Repos
def clone_repo(repo_url, dest_folder):
    try:
        print(f"Cloning repository from {repo_url} into {dest_folder}")
        Repo.clone_from(repo_url, dest_folder)
        print("Repository cloned successfully.")
    except Exception as e:
        print(f"An error occurred while cloning the repository: {e}")


# Function to stream the download of larger files
def stream_dl(url,file_name):
    # Open the stream to the URL
    r = requests.get(url, stream=True)

    print('Saving to: ', file_name)

    # Create the directory/file 
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024*1024):
            if chunk:
                print('#',end="",flush=True)
                f.write(chunk)
    print('\nSave Complete.\n')


# Function to Download and extract files
def get_and_extract(url, location, overwrite, basefolder=os.getcwd()):
    print('URL: ', url)
    element = ManifestItem(url,location,overwrite, basefolder)
    # this will return a tuple of root and extension
    split_tup = os.path.splitext(element.url)

    # extract the file name and extension
    url_base = split_tup[0]
    file_extension = split_tup[1]

    if os.path.exists(location):
        print("File exists...")
        print(location)
        if not element.overwrite:
            print("Overwrite flag set to FALSE")
            print("Existing file(s) will not be updated.")
            return
        else:
            print("Overwrite flag set to TRUE")
            print("Existing file(s) will be updated/overwritten")
    match element.item_type:
        case 'HF_FILE':
            if element.overwrite:
                print("Deleting existing file: " + element.location)
                if os.path.isfile(element.location):
                    try:
                        os.remove(element.location)
                    except OSError as e:
                        print("Error: %s - %s." % (e.filename, e.strerror))
                        
            repo_id = element.repo_id
            f_name = element.url_parts.path.split('/blob/main/')[1]
            l_dir = element.local_path + '/' + f_name

            enable_progress_bars()
            #hf_hub_download(repo_id=element.repo_id, filename=f_name) #download to the local cache first
            hf_hub_download(repo_id=element.repo_id,filename=f_name,local_dir=l_dir) #download to local directory, will used cached files
            #huggingface downloads download the directory, we'll need to fix this
            dir_root = element.local_path + '/' + f_name.split('/')[0]
            if os.path.exists(dir_root):
                if not os.path.isfile(dir_root):    
                    #os.rename(dir_root, element.local_path+"/delete")
                    shutil.move(element.local_path +'/'+ f_name +'/'+ f_name, element.local_path + '/file.tmp')
                    shutil.rmtree(element.local_path+'/'+f_name.split('/')[0])
                    shutil.move(element.local_path + '/file.tmp', element.location)
        case 'CM_MANAGER_INSTALL':
            subprocess.call([sys.executable, './ComfyUI/custom_nodes/ComfyUI-Manager/cm-cli.py','install',element.url])


        case 'HF_REPO':
            include_list = ['*.*']
            exclude_list = ['*.md']
            enable_progress_bars()
            #check url querystring for inclusion/exclusions
            if len(element.url_parts.query): #If the query portion is not empty
                query_args=element.url_parts.query.split('&')
                for arg in query_args:
                    filter_key, filter_mask = arg.split('=')
                    filter_key = filter_key.lower().replace(' ','') #convert to lower and remove any whitespace
                    filter_mask = filter_mask.replace(' ','') #remove any whitespace
                    
                    
                    match filter_key:
                        case 'exclude':
                            exclude_list = exclude_list+filter_mask.split(',')

                        case 'include':
                            include_list = filter_mask.split(',')

            snapshot_download(repo_id=element.repo_id, local_dir=element.location, allow_patterns=include_list, ignore_patterns=exclude_list)

        case 'GH_FILE':
            stream_dl(element.url, element.location)

        case 'GH_REPO':
            manage_package(element.repo_id,element.url,element.location)

        case 'UNDEFINED' | 'LOCAL_FILE':
            match file_extension:
                case '.zip':
                    if element.item_type == 'LOCAL_FILE':
                        z = zipfile.ZipFile(element.url, mode='r')
                    else:
                        # Get the URL
                        r = requests.get(url)
    
                        print('Extracting to: ', location)
    
                        # Stream the URL into the Zip Decompressor
                        z= zipfile.ZipFile(io.BytesIO(r.content))
                        
                    z.extractall(location)
                    print('Extraction complete.\n')

                # case '.7z':
                    # # 7z needs to save the file first
                    # if element.item_type == 'LOCAL_FILE':
                        # archive = py7zr.SevenZipFile(element.url, mode='r')
                    # else:
                        # temp_store = './'+url.rsplit('/',1)[1]
                        # stream_dl(url, temp_store)
                        # archive = py7zr.SevenZipFile(temp_store, mode='r')
                    # archive.extractall(path=location)
                    # archive.close()
                case '.py':
                    # case to handle processing py files for additional functionality needs
                    if element.item_type == 'LOCAL_FILE':   
                        exec(open(element.url).read(), globals())
                    else:
                        stream_dl(url,location)

                # Not an archive
                case _:
                    if element.item_type == 'LOCAL_FILE':
                        shutil.copyfile(element.url,element.location)
                    else:
                        stream_dl(url,location)


#If the custom CSV file is a relative filepath, convert it to absolute.
#This file pathpath must be set BEFORE changing the working directory.
manifestFile = './install_files.csv'
if not os.path.isabs(manifestFile):
    manifestFile=os.path.abspath(manifestFile)

#Change the working directory to the install folder directory
installFolder = os.path.normpath(os.path.join(os.getcwd(),'ComfyUI_windows_portable'))
print('Change the working folder to: '+installFolder)
os.chdir(installFolder)

    
baseFolder = os.path.normpath(os.getcwd())

# Now get the ComfyManager from it's git repo
repository_url = "https://github.com/ltdrdata/ComfyUI-Manager.git"
# Where ComfyManager will go
destination_folder = "./ComfyUI/custom_nodes/ComfyUI-Manager"
# Create the target directory
os.makedirs(os.path.dirname(destination_folder), exist_ok=True)
# Cloning the repository
manage_package('ComfyUI-Manager',repository_url, destination_folder)
subprocess.call([sys.executable, '-m', 'pip', 'install','-r','./ComfyUI/custom_nodes/ComfyUI-Manager/requirements.txt'])

# Load the CSV file and iterate over each line
print(manifestFile)

user_profile = os.environ.get('USERPROFILE')


with open(manifestFile, mode ='r')as file:
    csvFile = csv.reader(file)
    for lines in csvFile:
        get_and_extract(lines[0], lines[1], lines[2], baseFolder)


#Install Complete
comfyui_path = Path('./ComfyUI')
#print(f'ComfyUI_PATH = {comfyui_path}')
comfyui_python_path = Path('./python_embeded')
#print(f'ComfyUI_PYTHON = {comfyui_python_path}')
print('Installation is complete....')
print('***********************************************************************')
print('The path information below can be used to setup the ComfyUI BlenderAI node Addon in Blender 3D')
print('')
print(f'ComfyUI Path =  {comfyui_path.resolve()}\\')
print(f'Python Path =  {comfyui_python_path.resolve()}\\')
print('***********************************************************************')
print('Press any key to finish...')
msvcrt.getch() # wait for a key press