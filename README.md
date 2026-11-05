# AutoScrape Pro — Telangana Vehicle Registration Intelligence System

Automated high-precision scraper for vehicle registration particulars, owner details, and specs from the Telangana Transport Portal.

---

## 💻 Option 1: Run Locally (Without Docker)

You can install all libraries and run the app directly on your machine using our one-click runner scripts.

### 🍏 On macOS / Linux:

1. Make sure Python 3 is installed (`python3 --version`).
2. Open **Terminal** in the project folder and run:
   ```bash
   bash run_mac.sh
   ```
   *(This automatically creates a virtual environment, installs `pandas`, `openpyxl`, `streamlit`, `playwright`, downloads Chromium, and starts the app).*

---

### 🪟 On Windows:

1. Make sure Python is installed from [python.org](https://www.python.org/downloads/) (ensure **"Add Python to PATH"** is checked during installation).
2. Simply **double-click** the file:
   ```
   run_windows.bat
   ```
   *(Or open PowerShell / Command Prompt in this folder and type `run_windows.bat`).*
   *(It will automatically create the environment, install all libraries, download Chromium, and launch the app in your browser).*

---

## 🐳 Option 2: Run with Docker

If you prefer zero manual installation and want to run it via container:

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and start it.
2. In the project directory, run:
   ```bash
   docker compose up -d
   ```
3. Open **`http://localhost:8501`** in your browser.
4. To stop: `docker compose down`.
