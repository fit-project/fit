![FIT Banner](./assets/branding/banner.png)

# FIT – Freezing Internet Tool

**FIT** is a Python 3 application for forensic acquisition of online content, including web pages, emails, and social media.

The project is based on the [final exam](https://github.com/zitelog/fit) by **Fabio Zito (@zitelog)** for the Master's program in **Cybersecurity, Digital Forensics, and Data Protection**.

---

## Technologies Used
- **MVC Pattern** for design
- **Python** as the programming language
- **[Qt](https://www.qt.io/download-open-source)** for the graphical user interface and Web Engine
- **Scapy** for network traffic capture
- **[Qt Multimedia](https://doc.qt.io/qt-6/qtmultimedia-index.html)** for screen video and audio recording
  - More information about audio recording [here](https://github.com/fit-project/fit/wiki/Screen-recording-audio-management)
- **SQLite and SQLAlchemy** for data management

---

## Prerequisites
Before installing FIT, make sure you have the following dependencies installed:

- **[FFmpeg](https://ffmpeg.org/download.html)** (required for screen recording and media processing)
- **[NPCAP](https://npcap.com/dist/)** (required only for Windows, to capture network traffic and execute traceroute)  
  **Note:** Do not install WinPCAP as it is deprecated.

---

## What’s new in 3.0.0

Starting from **v3.0.0**, FIT becomes a **bundle/launcher**. Each acquisition module lives in its own repository and can be installed or updated independently.

### External Modules (installed via Poetry Git dependencies)
- **fit-wizard** – guided flow and common UI
- **fit-web** – generic web acquisitions
- **fit-mail** – email acquisitions
- **fit-instagram** – Instagram acquisitions
- **fit-video** – Video acquisitions
- **fit-entire_website** – Whole-site acquisitions

This modular architecture allows investigators to:
- Install only the required modules.
- Update each module independently.
- Develop, test, and release modules on separate timelines.

---

## Installation (Bundle)

```bash
git clone https://github.com/fit-project/fit.git
cd fit
pip install poetry
poetry install
poetry run python fit.py
```

---

## Installation (Single Module)

Each module can be installed as a standalone package. For example:

```bash
pip install poetry
poetry add git+https://github.com/fit-project/fit-web.git@main
```

---
