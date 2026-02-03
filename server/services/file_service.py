import os
from typing import List, Dict, Any
from supabase import create_client, Client


class FileService:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    def save_file_record(self, user_id: str, filename: str, original_filename: str, 
                        file_path: str, file_size: int, mime_type: str, bucket: str) -> Dict[str, Any]:
        """
        Save file metadata to database
        """
        try:
            response = self.supabase.table("files").insert({
                "user_id": user_id,
                "filename": filename,
                "original_filename": original_filename,
                "file_path": file_path,
                "file_size": file_size,
                "mime_type": mime_type,
                "bucket": bucket
            }).execute()
            
            return {
                "success": True,
                "file": response.data[0] if response.data else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_user_files(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all files uploaded by a specific user
        """
        try:
            response = self.supabase.table("files").select("*").eq("user_id", user_id).order("uploaded_at", desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            return []
    
    def delete_file_record(self, file_id: str, user_id: str) -> Dict[str, Any]:
        """
        Delete file record from database (only if owned by user)
        """
        try:
            response = self.supabase.table("files").delete().eq("id", file_id).eq("user_id", user_id).execute()
            
            return {
                "success": True,
                "deleted": len(response.data) > 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
