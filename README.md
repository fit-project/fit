# FIT – Freezing Internet Tool

The project is based on the final exam by **Fabio Zito (@zitelog)** for the Master's program in **Cybersecurity, Digital Forensics, and Data Protection**.

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

## Migration from 2.x to 3.0.0

| Component | Status | Notes |
|------------|---------|-------|
| Core logic | Refactored | FIT acts as a launcher |
| GUI | Moved | Now in `fit-wizard` |
| Web module | Externalized | `fit-web` repo |
| Instagram module | Externalized | `fit-instagram` repo |
| Mail module | Externalized | `fit-mail` repo |
| Video module | Externalized | `fit-video` repo |
| Entire website module | Externalized | `fit-entire_website` repo |

---

## Repository Links

| Module | Repository |
|---------|-------------|
| fit-wizard | [https://github.com/fit-project/fit-wizard](https://github.com/fit-project/fit-wizard) |
| fit-web | [https://github.com/fit-project/fit-web](https://github.com/fit-project/fit-web) |
| fit-mail | [https://github.com/fit-project/fit-mail](https://github.com/fit-project/fit-mail) |
| fit-instagram | [https://github.com/fit-project/fit-instagram](https://github.com/fit-project/fit-instagram) |
| fit-video | [https://github.com/fit-project/fit-video](https://github.com/fit-project/fit-video) |
| fit-entire_website | [https://github.com/fit-project/fit-entire_website](https://github.com/fit-project/fit-entire_website) |

---
