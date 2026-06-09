import { useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import './App.css'

const SESSION_TOKEN_KEY = 'access_token'
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const isAuthenticated = () => Boolean(sessionStorage.getItem(SESSION_TOKEN_KEY))

function LoginPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (isAuthenticated()) {
    return <Navigate to="/welcome" replace />
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(data.detail || 'No fue posible iniciar sesión')
      }

      sessionStorage.setItem(SESSION_TOKEN_KEY, data.access_token)
      navigate('/welcome', { replace: true })
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page-shell">
      <section className="card-shell">
        <div className="card-surface">
          <h1>Iniciar sesión</h1>
          <p className="subtitle">Ingresa tus credenciales para continuar.</p>

          <form className="login-form" onSubmit={handleSubmit}>
            <label htmlFor="username">Usuario</label>
            <input
              id="username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />

            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />

            <button type="submit" disabled={loading}>
              {loading ? 'Ingresando...' : 'Ingresar'}
            </button>
          </form>

          {error ? (
            <p className="error" role="alert">
              {error}
            </p>
          ) : null}
        </div>
      </section>
    </main>
  )
}

function WelcomePage() {
  const navigate = useNavigate()

  const handleLogout = () => {
    sessionStorage.removeItem(SESSION_TOKEN_KEY)
    navigate('/login', { replace: true })
  }

  return (
    <main className="page-shell">
      <section className="card-shell">
        <div className="card-surface">
          <h1>Bienvenido</h1>
          <p className="subtitle">Tu sesión está activa correctamente.</p>
          <button type="button" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </div>
      </section>
    </main>
  )
}

function ProtectedRoute({ children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }

  return children
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/welcome"
          element={
            <ProtectedRoute>
              <WelcomePage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to={isAuthenticated() ? '/welcome' : '/login'} replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
