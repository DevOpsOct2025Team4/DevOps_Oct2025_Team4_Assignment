import os
from typing import Optional, Dict, Any
from supabase import create_client, Client


class AuthService:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password
        Returns user data and session tokens
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "role": response.user.user_metadata.get("role", "user")
                    },
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid credentials"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def logout(self, access_token: str) -> Dict[str, Any]:
        """
        Logout user by invalidating their session
        """
        try:
            # Set the session first
            self.supabase.auth.set_session(access_token, access_token)
            self.supabase.auth.sign_out()
            return {
                "success": True,
                "message": "Logged out successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify access token and return user data
        """
        try:
            response = self.supabase.auth.get_user(access_token)
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "role": response.user.user_metadata.get("role", "user")
                }
            return None
        except Exception:
            return None
    
    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        """
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            
            if response.session:
                return {
                    "success": True,
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to refresh session"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
