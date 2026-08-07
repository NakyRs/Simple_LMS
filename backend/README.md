# My Project

## Project Structure

```text
my-project/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   └── products.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── product.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   └── product.py
│   │   │
│   │   ├── services/
│   │   │   ├── user_service.py
│   │   │   └── product_service.py
│   │   │
│   │   ├── database.py
│   │   ├── config.py
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
* **routers/** : API endpoint definitions.
* **models/** : Database models.
* **schemas/** : Pydantic request/response schemas.
* **services/** : Business logic.
* **database.py** : Database configuration.
* **config.py** : Environment configuration.
* **main.py** : FastAPI application entry point.

### Frontend

* **src/** : Application source code.
* **public/** : Static assets.
* **package.json** : Project dependencies and scripts.
* **vite.config.js** : Vite configuration.
