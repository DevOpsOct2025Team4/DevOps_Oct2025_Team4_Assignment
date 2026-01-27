import uuid

import requests
from werkzeug.utils import secure_filename


class UploadError(RuntimeError):
    def __init__(self, status_code: int, detail: str):
        super().__init__("Supabase upload failed")
        self.status_code = status_code
        self.detail = detail


def upload_file_to_supabase(file, supabase_url: str, service_key: str, bucket: str, is_public: bool):
    safe_name = secure_filename(file.filename) or "upload"
    object_name = f"{uuid.uuid4().hex}_{safe_name}"
    base_url = supabase_url.rstrip("/")
    upload_url = f"{base_url}/storage/v1/object/{bucket}/{object_name}"

    headers = {
        "Authorization": f"Bearer {service_key}",
        "apikey": service_key,
        "Content-Type": file.mimetype or "application/octet-stream",
        "x-upsert": "false",
    }

    response = requests.put(upload_url, headers=headers, data=file.stream)
    if not response.ok:
        raise UploadError(response.status_code, response.text)

    payload = {
        "bucket": bucket,
        "path": object_name,
    }
    if is_public:
        payload["url"] = f"{base_url}/storage/v1/object/public/{bucket}/{object_name}"

    return payload
