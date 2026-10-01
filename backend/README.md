# Backend
## Project Structure

```text
root-project/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── db.py
│   │   │   └── security.py
│   │   │
│   │   ├── routers/
│   │   │   ├── auth/
│   │   │   ├── admin/
│   │   │   ├── instructor/
│   │   │   └── student/
│   │   │
│   │   ├── service/
│   │   │
│   │   ├── init_data.py
│   │   ├── models.py
│   │   └── main.py
│   │
│   ├── venv/
│   ├── requirements.txt
│   ├── .env
│   └── .gitignore
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── README.md
└── .gitignore
```

## Directory Description

### Backend

* **app/** : Main FastAPI application.
* **core/** : Database & Environment configuration
* **routers/** : API endpoint definitions.
* **services/** : Business logic.
* **init_data.py** : Initial data.
* **models.py** : Database models.
* **main.py** : FastAPI application entry point.

### Frontend

* **src/** : Application source code.
* **public/** : Static assets.
* **package.json** : Project dependencies and scripts.
* **vite.config.js** : Vite configuration.
