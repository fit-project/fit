# FIT 2.X.X — End of Support Notice

The 2.X.X release line of **FIT (Freezing Internet Tool)** contains several known bugs and architectural limitations.  
For this reason, the project is now being **redesigned into a modular suite**, which will officially debut with **FIT 3.0.0**.

---

## Transition to FIT 3.0.0

Starting from version **3.0.0**, FIT will no longer be a single monolithic application,  
but a **modular suite** composed of several independent Python packages — each focused on a specific type of acquisition.

Each module can be installed and executed separately, or as part of the complete FIT suite.

### FIT Modular Repositories Overview

| Module | Repository | Dependencies | Status |
|---------|-------------|---------------|---------|
| `fit-web` | [fit-project/fit-web](https://github.com/fit-project/fit-web) | `fit-scraper` | Created |
| `fit-mail` | [fit-project/fit-mail](https://github.com/fit-project/fit-mail) | `fit-scraper` | Created |
| `fit-instagram` | [fit-project/fit-instagram](https://github.com/fit-project/fit-instagram) | `fit-scraper` | Not created |
| `fit-video` | [fit-project/fit-video](https://github.com/fit-project/fit-video) | `fit-scraper` | Not created |
| `fit-entire_website` | [fit-project/fit-entire_website](https://github.com/fit-project/fit-entire_website) | `fit-scraper` | Not created |
| `fit-bootstrap` | [fit-project/fit-bootstrap](https://github.com/fit-project/fit-bootstrap) | — | Not created |
| `fit-scraper` | [fit-project/fit-scraper](https://github.com/fit-project/fit-scraper) | `fit-acquisition` | Created |
| `fit-acquisition` | [fit-project/fit-acquisition](https://github.com/fit-project/fit-acquisition) | `fit-cases` | Created |
| `fit-cases` | [fit-project/fit-cases](https://github.com/fit-project/fit-cases) | `fit-configurations` | Created |
| `fit-configurations` | [fit-project/fit-configurations](https://github.com/fit-project/fit-configurations) | `fit-assets`, `fit-common` | Created |
| `fit-assets` | [fit-project/fit-assets](https://github.com/fit-project/fit-assets) | — | Created |
| `fit-common` | [fit-project/fit-common](https://github.com/fit-project/fit-common) | — | Created |
| `fit-wizard` | [fit-project/fit-wizard](https://github.com/fit-project/fit-wizard) | `fit-verify-pdf-timestamp`, `fit-verify-pec` | Created |
| `fit-verify-pdf-timestamp` | [fit-project/fit-verify-pdf-timestamp](https://github.com/fit-project/fit-verify-pdf-timestamp) | `fit-cases` | Created |
| `fit-verify-pec` | [fit-project/fit-verify-pec](https://github.com/fit-project/fit-verify-pec) | `fit-cases` | Created |

---

### 🧠 Legend
- **Created** → Repository exists and is under development  
- **Not created** → Repository planned but not yet initialized  
- `—` → No dependencies


---

## Current status

- All **2.X.X versions are no longer supported** and will not receive further updates.  
- Users are encouraged to **download and test the new scrapers directly** from their repositories.  
- Each repository will soon provide **its own binary release**.  
- The main `fit` repository will include a **bundle binary** that integrates all modules.

---

## Stay updated
Follow the progress of the **FIT 3.0.0 modular release** in the official project board:  
[https://github.com/orgs/fit-project/projects/18](https://github.com/orgs/fit-project/projects/18)

---

### Credits
The FIT project is based on the final exam by **Fabio Zito (@zitelog)**  
for the Master's program in **Cybersecurity, Digital Forensics, and Data Protection**.
