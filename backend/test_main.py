import pytest
from fastapi.testclient import TestClient
from main import app, verify_password, create_access_token, verify_token
from datetime import timedelta

client = TestClient(app)


class TestAuthentication:
    """Test authentication endpoints and functions."""
    
    def test_login_success(self):
        """Test successful login with correct credentials."""
        response = client.post(
            "/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 300
    
    def test_login_invalid_password(self):
        """Test login with invalid password."""
        response = client.post(
            "/login",
            json={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "Incorrect" in response.json()["detail"]
    
    def test_login_invalid_username(self):
        """Test login with non-existent username."""
        response = client.post(
            "/login",
            json={"username": "nonexistent", "password": "admin123"}
        )
        assert response.status_code == 401
        assert "Incorrect" in response.json()["detail"]
    
    def test_refresh_token_success(self):
        """Test successful token refresh."""
        # Get initial tokens
        login_response = client.post(
            "/login",
            json={"username": "admin", "password": "admin123"}
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh the token
        response = client.post(
            "/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 300
    
    def test_refresh_token_invalid(self):
        """Test refresh with invalid token."""
        response = client.post(
            "/refresh",
            json={"refresh_token": "invalid_token"}
        )
        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]
    
    def test_protected_endpoint_success(self):
        """Test accessing protected endpoint with valid token."""
        # Get token
        login_response = client.post(
            "/login",
            json={"username": "admin", "password": "admin123"}
        )
        access_token = login_response.json()["access_token"]
        
        # Access protected endpoint
        response = client.get(
            "/protected",
            headers={"Authorization": f"*** {access_token}"}
        )
        assert response.status_code == 200
        assert response.json()["username"] == "admin"
        assert "protected" in response.json()["message"].lower()
    
    def test_protected_endpoint_missing_token(self):
        """Test accessing protected endpoint without token."""
        response = client.get("/protected")
        assert response.status_code == 401
        assert "missing" in response.json()["detail"].lower()
    
    def test_protected_endpoint_invalid_format(self):
        """Test accessing protected endpoint with invalid header format."""
        response = client.get(
            "/protected",
            headers={"Authorization": "InvalidFormat"}
        )
        assert response.status_code == 401
        assert "Invalid authorization header format" in response.json()["detail"]
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["service"] == "jwt-auth-backend"
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "endpoints" in data


class TestPasswordFunctions:
    """Test password hashing and verification functions."""
    
    def test_verify_password_correct(self):
        """Test verifying correct password."""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed = pwd_context.hash("admin123")
        assert verify_password("admin123", hashed)
    
    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed = pwd_context.hash("admin123")
        assert not verify_password("wrongpassword", hashed)
    
    def test_verify_password_empty(self):
        """Test verifying empty password."""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed = pwd_context.hash("admin123")
        assert not verify_password("", hashed)


class TestTokenFunctions:
    """Test JWT token creation and verification functions."""
    
    def test_create_access_token(self):
        """Test creating access token."""
        token = create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(seconds=300)
        )
        assert token is not None
        assert isinstance(token, str)
        assert "." in token  # JWT format check
    
    def test_verify_token_valid(self):
        """Test verifying valid token."""
        token = create_access_token(
            data={"sub": "testuser"},
            expires_delta=timedelta(seconds=300)
        )
        payload = verify_token(token)
        assert payload["sub"] == "testuser"
    
    def test_verify_token_invalid(self):
        """Test verifying invalid token."""
        with pytest.raises(Exception):  # Should raise HTTPException
            verify_token("invalid_token")
    
    def test_token_expiration(self):
        """Test that expired tokens are rejected."""
        from datetime import datetime, timezone, timedelta
        from jose import jwt
        from main import SECRET_KEY, ALGORITHM
        
        # Create token that expired 1 second ago
        payload = {
            "sub": "testuser",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        with pytest.raises(Exception):  # Should raise HTTPException
            verify_token(token)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
