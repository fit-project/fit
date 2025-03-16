![FIT Banner](./assets/branding/banner.png)

# Freezing Internet Tool (FIT)

**FIT** is a Python 3 application for forensic acquisition of online content, including web pages, emails, and social media.

The project is based on the [final exam](https://github.com/zitelog/fit) by **Fabio Zito (@zitelog)** for the Master's program in **Cybersecurity, Digital Forensics, and Data Protection**, supervised by Prof. **Giovanni Bassetti (@nannib)**.

## Technologies Used
- **MVC Pattern** for design
- **Python** as the programming language
- **[Qt](https://www.qt.io/download-open-source)** for the graphical user interface and Web Engine
- **Scapy** for network traffic capture
- **[Qt Multimedia](https://doc.qt.io/qt-6/qtmultimedia-index.html)** for screen video and audio recording
  - More information about audio recording [here](https://github.com/fit-project/fit/wiki/Screen-recording-audio-management)
- **SQLite and SQLAlchemy** for data management

## Prerequisites
Before installing FIT, make sure you have the following dependencies installed:

- **[FFmpeg](https://ffmpeg.org/download.html)** (required for screen recording and media processing)
- **[NPCAP](https://npcap.com/dist/)** (required only for Windows, to capture network traffic and execute traceroute)  
  **Note:** Do not install WinPCAP as it is deprecated.

## Cloning the GitHub Repository
To get the latest version of the source code:
```sh
git clone git@github.com:fit-project/fit.git fit
```

## Installation
Once you've downloaded FIT and installed all prerequisites:

1. Navigate to the project folder:
   ```sh
   cd fit
   ```
2. If you don't have [Poetry](https://python-poetry.org/), install it via pip:
   ```sh
   pip install poetry
   ```
3. Install dependencies:
   ```sh
   poetry install
   ```

## Running FIT
To see available options and parameters, run:
```sh
poetry run python fit.py -h
usage: fit.py [-h] [--with-ffmpeg] [--without-ffmpeg] [--with-npcap] [--without-npcap] [--debug] [fit_bootstrap_pid] [{user,admin}]

Start FIT application

positional arguments:
  fit_bootstrap_pid  FIT bootstrap process ID (default: None)
  {user,admin}       Specify user privileges:
                     - 'user' (default): Standard user mode.
                     - 'admin': The user executing FIT has administrative privileges.
                       If not running as admin, it will not be possible to capture network traffic and execute traceroute.

options:
  -h, --help         show this help message and exit
  --with-ffmpeg      Enable FFmpeg support for media processing. (default: False)
  --without-ffmpeg   Disable FFmpeg support (default). (default: False)
  --with-npcap       Enable Npcap support (only on Windows) to capture network traffic. (default: False)
  --without-npcap    Disable Npcap support (default, only on Windows). Without Npcap, it will not be possible to capture network traffic. (default: False)
  --debug            Enable debug mode. (default: False)
```
If no parameters are specified, FIT will run with default values:
```sh
poetry run python fit.py
```
