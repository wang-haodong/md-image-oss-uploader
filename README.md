# Markdown 图片批量上传与路径自动替换平台

本项目支持**批量上传 Markdown 文件和本地图片**，自动上传图片至云存储（支持 **阿里云 OSS** 或 **MinIO**），并将 Markdown 文件内所有本地图片路径自动替换为云端外链。

> **支持两种上传方式：**  
>
> 1. 文件夹上传（拖入整文件夹，适合单个 md 和配套图片）  
> 2. zip 包上传（zip 可包含多级子目录、多个 md 和图片，适合批量处理）

> **云存储类型可选 OSS 或 MinIO，切换仅需修改配置。**

---

## 功能亮点

- 一键上传 Markdown 及本地图片文件夹或 zip 包
- 自动解析 Markdown，提取所有本地图片引用
- 自动批量上传图片到云存储
- Markdown 图片路径自动替换为外链
- 支持批量处理多个 md 文件
- 支持多级子目录图片、文件名自动映射
- 上传结果和替换日志友好展示
- OSS / MinIO 存储类型配置一键切换

---

## 项目目录结构示例

```yaml
project-root/
├── app.py # FastAPI 主服务入口
├── utils.py # 存储&图片处理工具
├── config.py # 存储配置信息
├── requirements.txt # 项目依赖
├── static/
│ └── index.html # 前端页面
```

---

## 快速开始

### 1. 安装依赖

建议新建虚拟环境后：

---

## 快速开始

### 1. 安装依赖

建议新建虚拟环境后：

```bash
pip install -r requirements.txt
```

**requirements.txt 内容：**

```tex
fastapi>=0.110
uvicorn[standard]>=0.29
oss2>=2.18.0
minio>=7.1.16
python-multipart>=0.0.9
tqdm>=4.66.4
```

### 2. 配置存储

编辑 `config.py`，根据你的实际情况填写：

#### OSS 配置（适用阿里云 OSS）：

```
python


复制编辑
storage_type = "oss"
endpoint = "https://oss-cn-beijing.aliyuncs.com"
access_key_id = "你的AK"
access_key_secret = "你的SK"
bucket_name = "your-bucket"
object_prefix = "markdown/"
```

#### MinIO 配置（适用 MinIO/S3 兼容存储）：

```
python


复制编辑
storage_type = "minio"
minio_endpoint = "minio服务器地址:端口"
minio_access_key = "minio的access_key"
minio_secret_key = "minio的secret_key"
minio_bucket_name = "你的bucket"
minio_secure = False   # True 为 https
object_prefix = "markdown/"
```

只需切换 `storage_type` 字段即可自动切换云存储类型。

------

### 3. 启动服务

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

------

### 4. 使用方式

#### - 访问前端页面

在浏览器中打开

```bash
http://localhost:8000/static/index.html
```

#### - 上传模式

- **文件夹上传**：适合一个 md 和相关图片的情况，选择模式“文件夹上传”，点按钮上传。
- **zip 上传**：适合批量 md + 图片，zip 可含多级文件夹，模式切换为“zip”，上传压缩包即可。

#### - 结果输出

- **文件夹上传**：处理结果为单个新的 md 文件，可直接下载。
- **zip 上传**：批量处理所有 md，打包成 zip 文件下载，日志随包返回。

------

## 详细功能说明

- **支持多 md 多图片批量处理**，zip 模式下所有 md 都会处理，图片支持多目录/同名
- **图片路径自动识别**，md 中图片相对路径、同名、不同目录都能准确匹配
- **云存储外链自动生成**，支持公网直链/自定义域名等，MinIO 如需签名请参见官方文档
- **自动处理未上传图片**，结果日志会提示哪些图片未找到或未上传
- **安全设计**，不会在前端暴露敏感信息，后端自动鉴权

------

## 常见问题

**Q1:** 上传失败，提示 Method Not Allowed？
 A: 检查后端路由和静态文件挂载，确认静态文件不要用根路径 `/` 挂载，前端 fetch 路径要用 `/api/process` 或 `/api/process_zip`。

**Q2:** MinIO 不能用？
 A: 确认 minio 服务可访问，config.py 配置无误，并 pip 安装 minio 库。

**Q3:** Markdown 路径没替换？
 A: 确认上传了所有图片文件（文件夹上传需全选图片，zip 模式需全部包含），否则未上传的图片路径不会被替换。

**Q4:** 上传大文件/大量文件超时？
 A: 推荐 zip 包上传，或调整 nginx/gunicorn/uvicorn 超时时间。OSS/MinIO 端亦可适当调大最大对象大小。

------

## 技术选型

- **FastAPI**：异步 Python Web 框架
- **OSS2**：阿里云 OSS Python SDK
- **minio**：MinIO Python SDK
- **Tailwind CSS**：前端样式
- **原生 JS**：前端逻辑，支持现代浏览器

------

## 贡献 & 定制

如需支持其他云存储（如七牛、腾讯云、AWS S3），可按 `utils.py` 扩展接口实现。
 如需前端支持更多格式、进度实时推送、鉴权等高级功能，请 fork 或提交 issue。

------

## License

MIT

------

> 本项目适用于知识文档管理、博客批量图床、文件迁移等场景，安全易用，欢迎 Star/Fork/自用/改造！