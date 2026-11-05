# 🍏 macOS / Linux Manual Setup & Run Commands

Follow these step-by-step commands in your **Terminal**.

---

## 1. Prerequisites
Ensure Python 3 is installed. Check by running:
```bash
python3 --version
```
*(If not installed, download from [python.org](https://www.python.org/downloads/) or run `brew install python`)*

---

## 2. Navigate to Project Directory
```bash
cd /path/to/AppScrapper
```

---

## 3. Create a Virtual Environment (Recommended)
This keeps your system Python clean and isolated:
```bash
python3 -m venv venv
```

---

## 4. Activate the Virtual Environment
```bash
source venv/bin/activate
```
*(Your terminal prompt should now show `(venv)` at the beginning).*

---

## 5. Install Required Libraries
```bash
pip install -r requirements.txt
```
*(Or manually install individually: `pip install streamlit playwright pandas openpyxl`)*

---

## 6. Install Playwright Chromium Browser
This downloads the headless Chromium browser used for scraping:
```bash
playwright install chromium
```

---

## 7. Run the Application
```bash
streamlit run app.py
```

The app will open automatically in your browser at:
**`http://localhost:8501`**

---

## 🔄 Daily / Future Runs
Once the first-time setup is done, you only need to run these 2 commands:
```bash
source venv/bin/activate
streamlit run app.py
```
*(To stop the app: press `Ctrl + C` in the Terminal).*
