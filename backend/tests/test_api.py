import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

# Now import app after path is set
from app.main import app

client = TestClient(app)

class TestAPI:
    """Basic API tests"""
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "TechKraft" in response.json()["message"]
    
    def test_register_endpoint_exists(self):
        response = client.post("/auth/register", json={
            "email": "testuser@example.com",
            "password": "password123",
            "full_name": "Test User"
        })
        # Should either succeed or fail with validation, but endpoint exists
        assert response.status_code in [201, 400, 422]
    
    def test_login_endpoint_exists(self):
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "wrong"
        })
        # Should return 401 (Unauthorized) not 404
        assert response.status_code == 401


class TestAuth:
    """Authentication tests"""
    
    def test_register_success(self):
        import uuid
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        
        response = client.post("/auth/register", json={
            "email": unique_email,
            "password": "password123",
            "full_name": "Test User"
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["role"] == "reviewer"
    
    def test_register_duplicate_email(self):
        email = "duplicate_test@example.com"
        
        # First registration
        client.post("/auth/register", json={
            "email": email,
            "password": "password123",
            "full_name": "First User"
        })
        
        # Second registration with same email
        response = client.post("/auth/register", json={
            "email": email,
            "password": "password123",
            "full_name": "Second User"
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_login_success(self):
        import uuid
        unique_email = f"login_{uuid.uuid4().hex[:8]}@example.com"
        
        # Register first
        client.post("/auth/register", json={
            "email": unique_email,
            "password": "password123",
            "full_name": "Login User"
        })
        
        # Then login
        response = client.post("/auth/login", json={
            "email": unique_email,
            "password": "password123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_invalid_password(self):
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401


class TestCandidates:
    """Candidate endpoint tests"""
    
    def setup_method(self):
        # Get admin token for tests
        response = client.post("/auth/login", json={
            "email": "admin@techkraft.com",
            "password": "Admin123!"
        })
        if response.status_code == 200:
            self.admin_token = response.json()["access_token"]
        else:
            self.admin_token = None
    
    def test_get_candidates_list(self):
        if not self.admin_token:
            pytest.skip("Could not get admin token")
        
        response = client.get(
            "/candidates",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
    
    def test_get_candidates_with_pagination(self):
        if not self.admin_token:
            pytest.skip("Could not get admin token")
        
        response = client.get(
            "/candidates?page=1&page_size=10",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
    
    def test_get_candidates_filter_by_status(self):
        if not self.admin_token:
            pytest.skip("Could not get admin token")
        
        response = client.get(
            "/candidates?status=new",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
    
    def test_candidate_detail_endpoint(self):
        if not self.admin_token:
            pytest.skip("Could not get admin token")
        
        # First get a candidate
        list_response = client.get(
            "/candidates",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        candidates = list_response.json().get("items", [])
        
        if candidates:
            candidate_id = candidates[0]["id"]
            response = client.get(
                f"/candidates/{candidate_id}",
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            assert response.status_code == 200
            assert "candidate" in response.json()
            assert "scores" in response.json()
        else:
            pytest.skip("No candidates found to test detail endpoint")


class TestRoleBasedAccess:
    """Role-based access control tests"""
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access protected endpoints"""
        response = client.get("/candidates")
        assert response.status_code == 401
    
    def test_reviewer_token_works(self):
        # Create a reviewer account first
        import uuid
        unique_email = f"reviewer_{uuid.uuid4().hex[:8]}@example.com"
        
        register_response = client.post("/auth/register", json={
            "email": unique_email,
            "password": "password123",
            "full_name": "Reviewer User"
        })
        
        if register_response.status_code == 201:
            token = register_response.json()["access_token"]
            # Try to access candidates with reviewer token
            response = client.get(
                "/candidates",
                headers={"Authorization": f"Bearer {token}"}
            )
            # Should be able to access (200) not 401
            assert response.status_code == 200
        else:
            pytest.skip("Could not create reviewer account")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])