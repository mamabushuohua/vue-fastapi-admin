from datetime import datetime, timezone

from app.log import logger
from app.models.admin import RefreshToken


async def cleanup_expired_tokens():
    """
    Clean up expired refresh tokens from the database.
    """
    try:
        now = datetime.now(timezone.utc)
        deleted_count = await RefreshToken.filter(expires_at__lt=now).delete()
        logger.debug(f"Cleaned up {deleted_count} expired refresh tokens")
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {str(e)}")
        return 0
