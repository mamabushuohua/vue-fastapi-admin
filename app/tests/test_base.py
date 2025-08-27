import pytest


from app.schemas.login import JWTOut


@pytest.mark.asyncio
class TestBaseModule:
    """Test cases for the base module"""

    async def test_jwt_out_schema(self):
        """Test JWTOut schema creation"""
        jwt_out = JWTOut(access_token="test_access_token", refresh_token="test_refresh_token", username="testuser")

        assert jwt_out.access_token == "test_access_token"
        assert jwt_out.refresh_token == "test_refresh_token"
        assert jwt_out.username == "testuser"

        # Test model_dump method
        data = jwt_out.model_dump()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "username" in data
