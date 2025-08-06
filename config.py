# -*- coding: utf-8 -*-
# config.py
# storage_type = "oss" 或 "minio"
storage_type = "oss"

# OSS配置
endpoint        = "https://oss-cn-hangzhou.aliyuncs.com"   
access_key_id   = "xxxxxxxxxxxxxx"
access_key_secret = "xxxxxxxxxxxxxx"
bucket_name     = "test"
object_prefix = "markdown/"   # 默认目录，可让前端覆盖

# MinIO配置
minio_endpoint = "minio服务器地址:端口"
minio_access_key = "minio的access_key"
minio_secret_key = "minio的secret_key"
minio_bucket_name = "你的bucket"
minio_secure = False   # True为https