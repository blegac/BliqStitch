# BliqStitch

Tool to stitch images from the Bliq microscope.

## Overview

This Python script integrates image stitching from z stack of images coming from Bliq microscope. It includes functionalities for selecting the most sharp image or generating Z-projections from image stacks, applying BaSiC correction, and performing grid/collection stitching using ImageJ/Fiji.

## Softwares Requirements


- Apache Maven
- OpenJDK

## Dependencies

- opencv-python
- numpy
- tifffile
- scyjava
- imagej
- tqdm
- basicpy
  
## Softwares Installation
### OpenJDK

1. Download JDK Development Kit: https://www.oracle.com/ca-fr/java/technologies/downloads/

2. Find the JDK Installation Directory
*First, you need to find out where the JDK is installed on your system. The default directory is usually C:\Program Files\Java\jdk_version\, where jdk_version is the version of the JDK you have installed.*
3. Set the JAVA_HOME Environment Variable:
   1.	Right-click on 'This PC' on the desktop or File Explorer, then click Properties.
   2.	Click on 'Advanced system settings' on the left panel.
   3.	Click on 'Environment Variables...' button at the bottom.
   4.	Under 'System Variables', click 'New...'.
   5.	Enter 'JAVA_HOME' as the variable name and the path to your JDK directory as the variable value. For example, if your JDK is installed in C:\Program Files\Java\jdk-xx, then enter that path.
   6.	Click 'OK' to close all of the dialogs.
4. Update PATH Environment Variable
   1.	Go back to the 'Environment Variables' window, and scroll to find the Path variable under 'System variables'.
   2.	Click on 'Edit...'.
   3.	Click 'New' and add %JAVA_HOME%\bin.
5. Restart Your Shell

*Close and reopen your terminal (or start a new session) so that the changes take effect.*


1. You can verify that JAVA_HOME is set correctly by opening a new terminal window and running:
````bash
echo %JAVA_HOME% 
````

### Installing Apache Maven
The installation of Apache Maven is a simple process of extracting the archive and adding the bin directory with the mvn command to the PATH.

Prerequisite:
- Have a JDK installation on your system. Either set the JAVA_HOME environment variable pointing to your JDK installation or have the java executable on your PATH.

Detailed steps are:

1. Download last version of Maven: https://maven.apache.org/download.cgi
2. Extract distribution archive in any directory
```bash
unzip apache-maven-x.x.x-bin.zip
```

or
```bash
tar xzvf apache-maven-x.x.x-bin.tar.gz
```
*Alternatively use your preferred archive extraction tool.*

3. Add the bin directory of the created directory apache-maven-x.x.x to the PATH environment variable.

4. Confirm with `mvn -v` in a new shell. 
The result should look similar to : 
```output
Apache Maven 3.9.7 (8b094c9513efc1b9ce2d952b3b9c8eaedaf8cbf0)
Maven home: C:\Program Files\apache-maven-3.9.7
Java version: 22.0.1, vendor: Oracle Corporation, runtime: C:\Program Files\Java\jdk-22
Default locale: fr_CA, platform encoding: UTF-8
OS name: "windows 11", version: "10.0", arch: "amd64", family: "windows"
```
### Python

Install Python. https://www.python.org/downloads/

### Microsoft C++ Build Tools

Install Microsoft C++ Build Tools. https://visualstudio.microsoft.com/fr/downloads/?q=build+tools

*During the installation, make sure to select the "Desktop development with C++" workload.*

### Miniconda

Install Miniconda on your system. Follow the instructions here: https://docs.conda.io/en/latest/miniconda.html

## Setup dependecies

1. Clone this repository:

   ```bash
   git clone https://github.com/blegac/BliqStitch
   ```

2. Start the Anaconda Prompt program and install all dependencies there.
3. Upgrade pip and setuptools
   ```bash
   pip install --upgrade pip setuptools
   ```
4. Install pyimage. The installation via pip does not seem to work at the moment, but conda is working. Thus:
    
   ```bash
   conda create -n bliq_stitch python=3.12
   conda activate bliq_stitch
   conda config --add channels conda-forge
   conda install -n bliq_stitch pyimagej openjdk=8
   ```

### Requirements
6. Install other dependencies into the conda environment using `pip` to install dependencies from `requirements.txt`:
   ```bash
   cd BliqStitch
   pip install -r requirements.txt
   ```

## Running the code

Start the BliqStitcher with a command line in Miniconda command prompt.

Launch a Anaconda Prompt (Miniconda3)
Activate your virtual environment:
   ```bash
   conda activate bliq_stitch
   ```

Go to the BliqStitcher/bliq_stitch folder:
   ```bash
   cd BliqStitcher
   cd bliq_stitch
   ```

Run the stitcher:
   ```bash
   python BliqStitch.py
   ```

## Example Usage

The folder **Example data** can be use to test the stitcher.

### Step 1: Mode Selection

Once the code is running, you will be prompted to choose between the following options:

- Most Sharp Image
   
   This mode allows you to select the sharpest image from the z-stack for each xy position, ensuring that the clearest image is used.

- Z Projection
   
   This mode allows you to perform a z projection of the z-stack for each xy position, creating a composite image that represents the entire stack.

### Step 2: Directory Selection

Next, you will need to select the directory containing the images to be stitched. Please choose the "Orca flash-Ch-1" folder as the directory folder.