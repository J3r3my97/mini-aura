"""
Firebase Authentication utilities
"""
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from config import FIREBASE_PROJECT_ID, FIREBASE_CREDENTIALS
from app.utils.firestore import get_or_create_user

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
_firebase_app = None

# HTTP Bearer token security scheme
security = HTTPBearer()


class AuthenticatedUser:
    """Authenticated user data from Firebase token"""

    def __init__(self, uid: str, email: Optional[str] = None, token: dict = None):
        self.uid = uid
        self.email = email
        self.token = token or {}


def initialize_firebase():
    """
    Initialize Firebase Admin SDK (called on app startup)

    Uses Application Default Credentials (ADC) by default, or explicit
    credentials if FIREBASE_CREDENTIALS is provided.

    Returns:
        Firebase app instance

    Raises:
        RuntimeError: If initialization fails
    """
    global _firebase_app

    if _firebase_app is not None:
        logger.info("Firebase Admin SDK already initialized")
        return _firebase_app

    try:
        if FIREBASE_CREDENTIALS:
            # Use explicit credentials
            cred = credentials.Certificate(FIREBASE_CREDENTIALS)
            _firebase_app = firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized with explicit credentials")
        else:
            # Use Application Default Credentials (ADC)
            _firebase_app = firebase_admin.initialize_app()
            logger.info("Firebase initialized with Application Default Credentials")

        return _firebase_app

    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}", exc_info=True)
        raise RuntimeError(f"Firebase initialization failed: {str(e)}")


async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthenticatedUser:
    """
    Verify Firebase ID token from Authorization header

    Args:
        credentials: HTTP Authorization credentials (Bearer token)

    Returns:
        AuthenticatedUser with uid and email

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        # Extract token
        id_token = credentials.credentials

        # Verify token with Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token)

        # Extract user info
        uid = decoded_token.get('uid')
        email = decoded_token.get('email')

        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        logger.info(f"Authenticated user: {uid} ({email})")

        return AuthenticatedUser(uid=uid, email=email, token=decoded_token)

    except auth.InvalidIdTokenError:
        logger.warning("Invalid Firebase ID token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    except auth.ExpiredIdTokenError:
        logger.warning("Expired Firebase ID token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired"
        )

    except auth.RevokedIdTokenError:
        logger.warning("Revoked Firebase ID token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has been revoked"
        )

    except HTTPException:
        # Re-raise HTTPExceptions
        raise

    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def get_current_user(
    auth_user: AuthenticatedUser = Depends(verify_firebase_token)
) -> dict:
    """
    Get or create user in Firestore

    Args:
        auth_user: Authenticated user from Firebase token

    Returns:
        User document from Firestore

    Raises:
        HTTPException: 500 if Firestore operation fails
    """
    try:
        # Get or create user in Firestore
        user = await get_or_create_user(auth_user.uid, auth_user.email or "")

        logger.info(f"Retrieved user from Firestore: {auth_user.uid}")

        return user

    except Exception as e:
        logger.error(f"Error getting user from Firestore: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )
