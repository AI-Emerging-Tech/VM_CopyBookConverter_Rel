# Copybook Aware EBCDIC Data Converter

## Introduction
Copybook Aware EBCDIC Data Converter is a tool to interpret COBOL copybook(s) and generate an equivalent XML Schema Definition (.XSD) using hybrid method powered by deterministic approach and Generative AI. The solution also has an EBCDIC converter, which converts IBM based EBCDIC binary encoded files to equivalent xml loads.

It enables seamless porting of mainframe data files to modern digital platforms.

## Purpose
In general, most of the mainframe systems use transactional data in IBM EBCDIC format conforming to COBOL copybook(s) structures. Modern platforms cannot directly read the transactional data in EBCDIC format and preferably need the data converted to XML data loads conforming to XSD so that it can be consumed in most of the modern platforms without loosing the original data structure.

### This solution provides:
* Automatic Copybook → XSD schema generation
* EBCDIC → XML transformation using copybook metadata
* Full support for COMP, COMP-3, DISPLAY, OCCURS, Nested groups and REDEFINE
* Schema-validated XML output
* Fully metadata-driven (no field-by-field coding)

## Workflows
* There are two distinct workflows. (1) Copybook to XSD converter (2) EBCDIC to XML converter

### Supported Copybook Features
| Feature | Support
| :--- | :---: |
| PIC X(n) | &#10004; |
| PIC 9(n) DISPLAY | &#10004; |
| PIC 9(n)V9(m) COMP-3 | &#10004; |
| PIC 9(n) COMP | &#10004; |
| OCCURS | &#10004; |
| Nested groups | &#10004; |
| REDEFINES | &#10004; |
| Decimal scale preservation | &#10004; |
| XSD numeric typing | &#10004; |

## Prerequisites
* This solution uses an implementation of ollama framework with qwen3.5:35b LLM in local/private environment. This is to ensure that no data is going out of the intended environment. 
* The solution expects that Ollama and Qwen model has already been installed in the local machine. Ollama implementation, is not included as part of this repository. You need to download and install ollama and an available LLM in your target environment. This solution was thoroughly tested using qwen3.5:35b LLM. If you would like to replace the LLM, you may easily do that and replace the reference link(s) in the code as required. Details on Ollama and how to install and configure Ollama are available at Ollama official site: https://ollama.com/
* This solution is strongly recommended to be deployed under Linux environment. However, it is compatible with Windows as well, though not thoroughly tested.
* For more details about dependencies, refer to requirements.txt
* Please note that the LLM is needed only for the workflow 1: Copybook to XSD converter. The workflow 2: EDCDIC to XML converter will work without LLM since it is built using pure deterministic approach.


## Installation and Running

### Downloading the repository to target machine (Windows specific)
* Install git, if not already installed. Use installables from official git website: https://git-scm.com/install/ Choose installables as per OS.
* Create a subdirectory for the project at a target location in the machine like C:\CBC
* The logged in user should have full rights to the directory and subdirectories. Provide permissions, if needed.
* Open windows CMD, change directory to project directory. For example: cd C:\CBC
* Clone the project repository to project directory using the command:
```
git clone <url of this repository> .
(note the . at the end. Use it if you want to clone the content without parent directory VM_CopyBookConverter_Rel)
```

### Installing python
* You have to install python (if not available already). This solution has been tested on python 3.14.0. Recommended to install the same version (or higher)
* At the command prompt, you may check the current version of python using the command: python -V
* If python not available, download the appropriate version of python and install from python official site: https://www.python.org/downloads/

### Creating environment and installation of required libraries (Windows specific)
* In order to facilitate different versions of libraries for diffeent applications on the same machine, it is recommended to create and environment and install the required libraries inside the environment. Also run the applications always under the same environment
* Change the current directory to the sourcecode directory. For example: cd C:\CBC\src
* if environment is not yet created, create environment using command:
```
python -m venv venv
```
* Then activate the environment using:
```
venv\Scripts\activate
```
* The command prompt should now look like: (venv) C:\CBCRel\src>

* Before installing required libraries, first check the version of pip and it is recommended to update pip to latest version before installing any libraries as follows:
```
pip --version
python -m pip install --upgrade pip
``` 
* Please note that use pip3 instead of pip if appropriate

* Now install the required libraries as follows:
```
pip install lxml
pip install pydantic
pip install pyyaml
pip install python-multipart
pip install requests
```
* YOU SHOULD BE READY TO RUN THE WORKFLOWS NOW!


### Running Workflow 1: Copybook to XSD Converter
* The copybook to xsd converter takes the following arguments:

```
--inputcopybook
  Required argument. This is to specify the input copybook file including path and full filename with extension. The current user should have access permission to the directory and file.
--outputxsd
  Required argument. This is to specify the output xsd file name including path and full filename with extension. The current user should have access permission to the directory.
--no-llm
  Optional argument. If you want to run the application with pure deterministic approach without assistance by LLM, you may use this option. Otherwise skip. Default is with LLM.
--no-pretty
  Optional argument. Pretty library is used to make the output more readable with indents. Default is to use this. If you want to disable this, you can use this argument (disabling can speed up processing of very large files)
--debug
  Optional argument. This is to run the application in debug mode. If you experience bugs or any issues, you may choose to add this argument to run the application in debug mode, which will give more insight to the error through additional print statements in console to interpret the error.

This repository has a single simple sample copybook named "HO3-POLICY.cpy". It is recommended to test this file once you installed the application
```
```
Example command to run the sample file:
Make sure that you are in src folder and you have activated the environment as explained above: Use the following command to run:
python -m converters.copybook_to_xsd --inputcopybook testrun/copybooks/HO3-POLICY.cpy --outputxsd testrun/xsd/HO3-POLICY.xsd
```
```
After the message on command prompt "[DONE] XSD generated...", the output will be written as testrun/xsd/HO3-POLICY.xsd
For your runs, replace the filenames accordingly
```

### Running Workflow 2: EBCDIC file to XML Converter
* The EBCDIC to xml converter takes the following arguments:

```
--data-dir
  Required argument. This is to specify the directory location of the EBCDIC file. The file inside the directory will be taken. The current user should have access permission to the directory and file.
--copybook
  Required argument. This is to specify the corresponding copybook file, in which the data structure is defined. Please note that the EBCDIC file should be in exact structure with respect to reference copybook. Otherwise it will flag errors. The current user should have access permission to the directory and file.
--output-dir
  Required argument. This is to specify the output directory, where the output xml should be written. The current user should have access permission to the directory.
--xsd
  Optional argument. If you wish to do a validation of the output xml with the corresponding xsd file, you can add this. If not provided (default), the validation step will be skipped. The current user should have access permission to the directory and file.
--debug
  Optional argument. This is to run the application in debug mode. If you experience bugs or any issues, you may choose to add this argument to run the application in debug mode, which will give more insight to the error through additional print statements in console to interpret the error.

This repository has a single simple sample EBCDIC named "ho3_ebcdic.dat". It is recommended to test this file once you installed the application


Example command to run the sample file:
Make sure that you are in src folder and you have activated the environment as explained above:

```
```
Use the following command to run (without xsd validation):
python -m converters.ebcdic_to_xml --data-dir testrun/ebcdic --copybook testrun/copybooks/HO3-POLICY.cpy --output-dir testrun/xml
```
```
Use the following command to run (with xsd validation):
python -m converters.ebcdic_to_xml --data-dir testrun/ebcdic --copybook testrun/copybooks/HO3-POLICY.cpy --output-dir testrun/xml --xsd testrun/xsd/HO3-POLICY.xsd
```
```
After the message on command prompt "Generated testrun\xml\ho3_ebcdic.xml", the output will be available as testrun/xml/ho3_ebcdic.xml

For your runs, replace the filenames accordingly
```

#### Contacts
* **Web:** https://www.valuemomentum.com
