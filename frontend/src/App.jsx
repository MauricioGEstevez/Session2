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

  const certifications = [
    {
      id: 1,
      title: 'Collaboration Communications Systems Engineer Associate',
      description: 'Microsoft 365 Certified',
      link: 'https://learn.microsoft.com/en-us/credentials/certifications/m365-collaboration-communications-systems-engineer/',
      color: 'green'
    },
    {
      id: 2,
      title: 'Copilot and Agent Administration Fundamentals',
      description: 'Microsoft 365 Certified',
      link: 'https://learn.microsoft.com/en-us/credentials/certifications/copilot-and-agent-administration-fundamentals/',
      color: 'blue'
    },
    {
      id: 3,
      title: 'Cloud and AI Security Engineer Associate',
      description: 'SC-500 Certification (Formerly AZ-500)',
      link: 'https://learn.microsoft.com/en-us/credentials/certifications/exams/sc-500/',
      color: 'green'
    },
    {
      id: 4,
      title: 'Cybersecurity Architect Expert',
      description: 'SC-100 Certification',
      link: 'https://learn.microsoft.com/en-us/credentials/certifications/exams/sc-100/',
      color: 'blue'
    }
  ]

  return (
    <main className="page-shell welcome-page">
      <section className="welcome-container">
        <div className="card-shell">
          <div className="card-surface">
            <h1>Bienvenido</h1>
            <p className="subtitle">Tu sesión está activa correctamente.</p>
            <button type="button" onClick={handleLogout}>
              Cerrar sesión
            </button>
          </div>
        </div>

        <div className="certifications-section">
          <h2>Certificaciones Microsoft 2026</h2>
          <div className="certifications-grid">
            {certifications.map((cert) => (
              <a
                key={cert.id}
                href={cert.link}
                target="_blank"
                rel="noopener noreferrer"
                className={`certification-card certification-${cert.color}`}
              >
                <h3>{cert.title}</h3>
                <p>{cert.description}</p>
                <span className="cert-link">Más información →</span>
              </a>
            ))}
          </div>
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
