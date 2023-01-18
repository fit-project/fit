# Freezing Internet Tool
`FIT` is a Python3 application for forensic acquisition of contents like web pages, emails, social media, etc. directly from the internet. 
It's based on Fabio Zito (**@zitelog**) [final exam](https://github.com/zitelog/fit) for a Master named in Cybersecurity, Digital Forensics and Data Protection where the relator was Prof. Giovanni Bassetti (**@nannib**).

For the implementation:
* MVC Pattern
* Python Language
* Qt as graphical user interface
* Pyshark (wrapper for Tshark) which a sniffer (similar to Sun's snoop or tcpdump)
* OpenVC and Pyautogui for screen capture
* Pywebcopy for save all resource (html, css, js, image, etc.)


## Prerequisites
Make sure you have installed all of the following prerequisites on your development machine:
* Wireshark - [Download & Install Wireshark](https://www.wireshark.org/download/). Network traffic analyzer, or "sniffer", for Linux, macOS, *BSD and other Unix and Unix-like operating systems and for Windows.

## Downloading FIT
There are two ways you can get the FIT:

### Cloning the github repository
The recommended way to get FIT is to use git to directly clone the FIT repository:

```
git clone git@github.com:fit-project/fit.git fit
```

This will clone the latest version of the FIT repository to a **fit** folder.


## Install
Once you've downloaded FIT and installed all the prerequisites:

* go in fit folder:
```
cd fit
```
* create a virtual environment with following command (below its showed windows OS and git-bash):
```
python -m venv env
```
* activate the virtual environment (below its showed windows OS and git-bash):
```
source ./env/Scripts/activate
```
* update pip in the virtual environment by running the following command:
```
python -m pip install --upgrade pip
```
* install the dependencies:
```
pip install -r requirements.txt
```
## Running FIT

Run your application:

```
python fit.py
```
