# Session2

Este repositorio contiene:

- `backend/`: API en FastAPI con autenticación JWT.
- `frontend/`: aplicación web en React con pantalla de login y página de bienvenida protegida.

## Funcionalidad del frontend

- Login contra `POST /login` del backend.
- Guarda el `access_token` en `sessionStorage`.
- Redirección automática:
  - si no hay sesión, solo se puede acceder a `/login`;
  - si hay sesión, se permite `/welcome`.
- Botón de cierre de sesión en la pantalla de bienvenida.

## Diseño

La interfaz del frontend sigue el estándar definido en `DESIGN.md`:

- paleta principal basada en `#0F172A`, `#64748B`, `#F1F5F9`, `#FAFAFA`;
- tipografía Inter;
- espaciado con ritmo base de 12px;
- superficie tipo “glass” con borde degradado y blur.

## Cómo ejecutar

### 1. Backend

```bash
cd backend
poetry install
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> Credenciales por defecto: `admin / admin123`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend disponible en `http://localhost:5173`.

## Rutas del frontend

- `http://localhost:5173/login`
- `http://localhost:5173/welcome` (protegida por sesión)
