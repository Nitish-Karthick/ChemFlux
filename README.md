# ChemFlux – Chemical Equipment Parameter Visualizer (Hybrid Web + Desktop)

Hybrid application that runs as both a Web app (React + Chart.js) and a Desktop app (PyQt5 + Matplotlib), backed by a common Django REST API. Users can upload CSV files of chemical equipment and view summaries, charts, history (last 5 datasets), and export a PDF report.

## Tech Stack
- Backend: Django + Django REST Framework, pandas, SQLite, reportlab
- Web: React (Vite) + react-chartjs-2 + Chart.js
- Desktop: PyQt5 + Matplotlib
- Data: pandas for CSV parsing and analytics


Screenshots!


Web:
<img width="2559" height="1219" alt="image" src="https://github.com/user-attachments/assets/930cc705-65fb-4aad-81a2-83480e1e5c1f" />
Desktop app:
<img width="2559" height="1455" alt="image" src="https://github.com/user-attachments/assets/7e552aed-01fb-4e9a-9e6d-91c451e84da4" />

## 🚀 Live Demos

* **Web App (Netlify):** [https://chemflux.netlify.app/](https://chemflux.netlify.app/)
* **Backend API (Render):** [https://chemflux.onrender.com/api/ping/](https://chemflux.onrender.com/api/ping/)

> **Note:** The backend is hosted on a free tier. Please click the **Backend API** link first to wake it up (it may take 30-60 seconds to load).

## 🔐 Demo Credentials
To test the live deployment, please use the following credentials:
* **Username:** `admin`
* **Password:** `Chemflux@12345`

## Project Structure
```
ChemFlux/
├─ backend/
│  ├─ manage.py
│  ├─ chemflux_backend/ (Django project)
│  ├─ api/ (Django app with endpoints)
│  └─ requirements.txt
├─ web/ (React app via Vite)
├─ desktop/ (PyQt5 desktop app)
├─ sample_equipment_data.csv
└─ README.md
```

## API Overview
Authentication: DRF Basic Authentication (username/password).

Endpoints:
- GET /api/ping/ – Health check (no auth required)
- POST /api/upload/ – Upload CSV file as form-data key `file` (auth required)
- GET /api/datasets/ – Last 5 datasets (auth required)
- GET /api/datasets/<id>/ – Dataset detail (auth required)
- GET /api/datasets/<id>/report/ – PDF report (auth required)

Summary fields returned include:
- `total_count`
- `averages` (numeric column means)
- `type_distribution` (distribution by Type column if present)
- `columns` and `preview` (first 10 rows)

## Prerequisites
- Python 3.12 (project is tested with 3.12 using the `venv312` virtual environment)
- Node.js 18+
- Git (optional for submission)

## Backend – Local Setup (Windows PowerShell)
From the project root `ChemFlux/`:

1) Activate the pre-created Python 3.12 virtual environment (`venv312`)
```
./venv312/Scripts/Activate.ps1
```

2) Install Python dependencies (first time only)
```
pip install -r backend/requirements.txt
pip install -r desktop/requirements.txt
```

3) Initialize database and create a user
```
python backend/manage.py makemigrations
python backend/manage.py migrate
python backend/manage.py createsuperuser
```
Note the username/password; this will also be used to sign in from the Web and Desktop apps.

4) Run the API server
```
python backend/manage.py runserver
```
The API will be available at http://127.0.0.1:8000/ (Ping: http://127.0.0.1:8000/api/ping/)

Media uploads will be stored under `backend/media/uploads/`.

## Web App – Local Setup
In a separate terminal window:

1) Install dependencies
```
cd web
npm install
```

2) Start the dev server
```
npm run dev
```
The app will open on http://127.0.0.1:5173. Sign in using the Django user you created.

Features:
- Login with Basic Auth
- Upload CSV (try `../sample_equipment_data.csv`)
- View summary and charts
- History (last 5)
- Download PDF report

## Desktop App – Local Setup
The desktop app uses the same `venv312` environment and backend API.

1) Ensure `venv312` is activated (see Backend section).

2) Run the desktop app
```
python desktop/main.py
```
- Use the same username/password from Django.
- The desktop app hits the same API (configurable by env var `CHEMFLUX_API`, default `http://127.0.0.1:8000/api`).

## Quick Start – Launch Everything

1) **Start backend (API)**
- Open PowerShell in project root
- Activate env and run server:
  ```
  ./venv312/Scripts/Activate.ps1
  python backend/manage.py runserver
  ```

2) **Start web app**
- Open another PowerShell window in `web/`:
  ```
  cd web
  npm install   # first time only
  npm run dev
  ```
- Open http://127.0.0.1:5173 and log in with your Django user.

3) **Start desktop app (optional)**
- In a third PowerShell window from project root (with `venv312` activated):
  ```
  ./venv312/Scripts/Activate.ps1
  python desktop/main.py
  ```
- Log in with the same Django user. Both web and desktop will talk to the same API and share datasets/history.

## Optional: Deploy Web App to Netlify

You can deploy only the **web** frontend (React + Vite) as a static site on Netlify.

1) **Netlify site settings**
- New Site from Git → select this repo.
- **Base directory**: `web`
- **Build command**: `npm run build`
- **Publish directory**: `dist`

2) **Configure backend API URL**
- In Netlify → Site settings → Environment variables:
  - Add `VITE_API_BASE` with the full URL of your Django API, for example:
    - `https://your-backend-domain.com/api`
  - This is read by `web/src/api.js` and falls back to `http://127.0.0.1:8000/api` for local dev.

3) **CORS configuration**
- In `backend/chemflux_backend/settings.py`, add your Netlify URL (e.g. `https://your-site.netlify.app`) to `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` if you host the backend publicly.

Netlify will rebuild the site on every push to the selected branch.

## Notes & Assumptions
- DRF is configured with only BasicAuthentication to avoid CSRF for API POSTs from non-browser clients.
- CORS is enabled for common dev ports (5173, 3000). Adjust in `backend/chemflux_backend/settings.py` as needed.
- The backend stores only the last 5 datasets and deletes older ones automatically.
- The PDF is generated via reportlab with core summary data.
Screenshots!
Web:
![Uploading image.png…]()
