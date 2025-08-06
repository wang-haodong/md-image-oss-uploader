import re
import uuid
from pathlib import Path
from urllib.parse import urlparse

import config

MD_IMG_RE   = re.compile(r"!\[[^\]]*\]\((.*?)\)")
HTML_IMG_RE = re.compile(r'<img\s+[^>]*src=["\']([^"\']+)["\']')

def is_local(path: str) -> bool:
    return not path.startswith(("http://", "https://", "//"))

def iter_local_images(md_text: str):
    for pat in (MD_IMG_RE, HTML_IMG_RE):
        for m in pat.finditer(md_text):
            p = m.group(1).strip()
            if is_local(p):
                yield m, p

def get_bucket():
    if getattr(config, "storage_type", "oss") == "oss":
        import oss2
        auth = oss2.Auth(config.access_key_id, config.access_key_secret)
        return oss2.Bucket(auth, config.endpoint, config.bucket_name)
    else:  # minio
        from minio import Minio
        client = Minio(
            config.minio_endpoint,
            access_key=config.minio_access_key,
            secret_key=config.minio_secret_key,
            secure=getattr(config, "minio_secure", False),
        )
        # 自动建桶（如果没建的话）
        found = client.bucket_exists(config.minio_bucket_name)
        if not found:
            client.make_bucket(config.minio_bucket_name)
        return client

def upload_image(bucket, file_bytes: bytes, suffix: str, prefix: str):
    key = f"{prefix}{uuid.uuid4().hex}{suffix.lower()}"
    if getattr(config, "storage_type", "oss") == "oss":
        bucket.put_object(key, file_bytes)
        host = urlparse(config.endpoint).netloc
        return f"https://{config.bucket_name}.{host}/{key}"
    else:
        from minio.error import S3Error
        # put_object(bucket_name, object_name, data, length)
        bucket.put_object(
            config.minio_bucket_name,
            key,
            io.BytesIO(file_bytes),
            length=len(file_bytes),
            content_type="image/" + suffix.lower().replace(".", "")
        )
        # 生成外链（假设你设置了外部域名或直接用minio原生域名端口访问）
        # 你可以根据实际部署改成反向代理域名
        return f"http{'s' if getattr(config, 'minio_secure', False) else ''}://{config.minio_endpoint}/{config.minio_bucket_name}/{key}"
