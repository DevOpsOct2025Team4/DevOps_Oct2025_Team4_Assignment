import os
from typing import Optional, Dict, Any
from supabase import create_client, Client


class AuthService:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def _admin_client(self) -> Client:
        """
        Create a fresh admin client using the service role key.
        This avoids session contamination from user auth flows.
        """
        return create_client(self.supabase_url, self.supabase_key)

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password
        Returns user data and session tokens
        """
        try:
            response = self.supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if response.user and response.session:
                # Get role from user metadata
                user_meta = response.user.user_metadata or {}
                role = user_meta.get("role", "user")

                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "role": role,
                    },
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                    },
                }
            else:
                return {"success": False, "error": "Invalid credentials"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def logout(self, access_token: str, refresh_token: str) -> Dict[str, Any]:
        """
        Logout user by invalidating their session
        """
        try:
            # Set the session first
            self.supabase.auth.set_session(access_token, refresh_token)
            self.supabase.auth.sign_out()
            return {"success": True, "message": "Logged out successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify access token and return user data
        """
        try:
            response = self.supabase.auth.get_user(access_token)

            if response.user:
                # Try to get role from user_metadata, with fallback to raw_user_meta_data
                user_meta = response.user.user_metadata or {}
                role = user_meta.get("role", "user")

                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "role": role,
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
                        "refresh_token": response.session.refresh_token,
                    },
                }
            else:
                return {"success": False, "error": "Failed to refresh session"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_all_users(self) -> Dict[str, Any]:
        """
        Fetch all registered user accounts from Supabase auth
        Returns list of users with id, email, and role
        """
        try:
            admin_client = self._admin_client()
            response = admin_client.auth.admin.list_users()

            users_list = []
            if hasattr(response, "users") and response.users is not None:
                users_list = response.users
            elif isinstance(response, dict):
                users_list = response.get("users", [])
            elif isinstance(response, list):
                users_list = response

            if users_list:
                users = []
                for user in users_list:
                    users.append(
                        {
                            "id": user.id,
                            "email": user.email,
                            "role": (
                                user.user_metadata.get("role", "user")
                                if user.user_metadata
                                else "user"
                            ),
                            "created_at": (
                                user.created_at.isoformat()
                                if hasattr(user, "created_at")
                                else None
                            ),
                        }
                    )
                return {
                    "success": True,
                    "users": users,
                }

            return {"success": True, "users": []}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_user(
        self, email: str, password: str, role: str = "user"
    ) -> Dict[str, Any]:
        """
        Create a new user account in Supabase
        Args:
            email: User's email address
            password: User's password
            role: User's role (default: "user", can be "admin")
        Returns:
            Dict with success status and user data or error message
        """
        try:
            # Create user with Supabase admin API
            admin_client = self._admin_client()
            response = admin_client.auth.admin.create_user(
                {
                    "email": email,
                    "password": password,
                    "email_confirm": True,
                    "user_metadata": {"role": role},
                }
            )

            if response.user:
                return {
                    "success": True,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "role": role,
                    },
                    "message": "User created successfully",
                }
            else:
                return {"success": False, "error": "Failed to create user"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """
        Delete a user account from Supabase
        Args:
            user_id: The ID of the user to delete
        Returns:
            Dict with success status or error message
        """
        try:
            admin_client = self._admin_client()
            admin_client.auth.admin.delete_user(user_id)
            return {"success": True, "message": "User deleted successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
