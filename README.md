# AutoScrape Pro — Telangana Vehicle Registration Intelligence System

Automated high-precision scraper for vehicle registration particulars, owner details, and specs from the Telangana Transport Portal.

---

## 🐳 Running with Docker (On Any Computer)

You can run this application on **Windows, macOS, or Linux** without installing Python or Playwright manually. All you need is **Docker Desktop**.

### Step 1: Install Docker on the other computer
- **Windows / Mac:** Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- **Linux:** Install `docker` and `docker-compose-plugin`.

---

### Step 2: Copy this project folder
Copy the entire `AppScrapper` folder to the target computer (via USB drive, ZIP file, or Git).

---

### Step 3: Run with Docker Compose (Recommended)
Open a terminal / PowerShell inside the project directory and run:

```bash
docker compose up -d
```

- This automatically builds the image, installs Playwright Chromium with all required OS libraries, and launches the app.
- Once running, open your browser and navigate to:
  **`http://localhost:8501`**

To stop the container:
```bash
docker compose down
```

---

### Alternative: Run with standard Docker CLI

1. **Build the image:**
   ```bash
   docker build -t autoscrape .
   ```

2. **Run the container:**
   ```bash
   docker run -d -p 8501:8501 --shm-size=1gb --name autoscrape-app autoscrape
   ```
   *(Note: `--shm-size=1gb` ensures parallel Chromium tabs have sufficient shared memory).*

3. Open **`http://localhost:8501`** in your browser.
