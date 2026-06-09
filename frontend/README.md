# Frontend (React)

Aplicación React con dos rutas:

- `/login`: autentica contra el backend (`POST /login`).
- `/welcome`: ruta protegida, solo accesible si existe token en `sessionStorage`.

## Desarrollo

```bash
npm install
npm run dev
```

La configuración de Vite incluye un proxy para el backend en `http://localhost:8000` usando la ruta `/api`.
