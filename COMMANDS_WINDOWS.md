# 🪟 Windows Manual Setup & Run Commands

Follow these step-by-step commands in **Command Prompt (CMD)** or **PowerShell**.

---

## 1. Prerequisites
Ensure Python is installed. Check by running:
```cmd
python --version
```
*(If not installed, download from [python.org](https://www.python.org/downloads/). During installation, **check the box: "Add Python to PATH"**).*

---

## 2. Navigate to Project Directory
```cmd
cd path\to\AppScrapper
```

---

## 3. Create a Virtual Environment (Recommended)
This creates an isolated environment for the project:
```cmd
python -m venv venv
```

---

## 4. Activate the Virtual Environment
- **If using Command Prompt (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **If using PowerShell:**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(Note: If PowerShell gives a script execution policy error, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` or just use standard CMD).*

*(Your prompt will now show `(venv)` at the beginning).*

---

## 5. Install Required Libraries
```cmd
pip install -r requirements.txt
```
*(Or manually install individually: `pip install streamlit playwright pandas openpyxl`)*

---

## 6. Install Playwright Chromium Browser
This downloads the headless Chromium browser used for scraping:
```cmd
playwright install chromium
```

---

## 7. Run the Application
```cmd
streamlit run app.py
```

The app will open automatically in your browser at:
**`http://localhost:8501`**

---

## 🔄 Daily / Future Runs
Once the first-time setup is completed, you only need to run these 2 commands:
- **On Command Prompt (CMD):**
  ```cmd
  venv\Scripts\activate
  streamlit run app.py
  ```
- **On PowerShell:**
  ```powershell
  .\venv\Scripts\Activate.ps1
  streamlit run app.py
  ```
*(To stop the app: press `Ctrl + C` in your command window).*
