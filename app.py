from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import tempfile
import zipfile
import io
import utils

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


@app.post("/api/process", response_class=JSONResponse)
async def process_markdown(
    markdown: UploadFile = File(...),
    images: Optional[List[UploadFile]] = File(default=None),
    prefix: str = Form("markdown/")
):
    content = await markdown.read()
    md_text = content.decode("utf-8")
    images = images or []
    bucket = utils.get_bucket()
    log = []
    replacements = []
    missing = []
    total = 0
    replaced = 0

    image_map = {}
    for img in images:
        image_map[img.filename] = img
        if "/" in img.filename:
            image_map[Path(img.filename).name] = img

    for match, img_path in utils.iter_local_images(md_text):
        total += 1
        img_name = img_path.lstrip("./").replace("\\", "/")
        img_file = (
            image_map.get(img_path)
            or image_map.get(img_name)
            or image_map.get(Path(img_path).name)
        )
        if not img_file:
            log.append(f"⚠️ 未上传图片: {img_path}")
            missing.append(img_path)
            continue
        try:
            img_bytes = await img_file.read()
            url = utils.upload_image(bucket, img_bytes, Path(img_file.filename).suffix, prefix)
            replacements.append((match.span(1), url))
            log.append(f"✅ 上传并替换: {img_path} → {url}")
            replaced += 1
        except Exception as e:
            log.append(f"❌ 上传失败 {img_path}: {e}")

    for (start, end), url in sorted(replacements, key=lambda x: x[0][0], reverse=True):
        md_text = md_text[:start] + url + md_text[end:]

    summary = [
        f"检测到图片 {total} 张",
        f"已上传替换 {replaced} 张",
        f"未上传图片 {len(missing)} 张"
    ]
    log = summary + log
    return {
        "new_markdown": md_text,
        "log": log
    }


@app.post("/api/process_zip")
async def process_zip(
    zipfile_: UploadFile = File(...),
    prefix: str = Form("markdown/")
):
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_data = await zipfile_.read()
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
            zf.extractall(tmpdir)
        base = Path(tmpdir)
        md_files = list(base.rglob("*.md"))
        img_files = [f for f in base.rglob("*") if f.suffix.lower() in {".jpg",".jpeg",".png",".gif",".bmp",".webp"}]

        img_map = {}
        for img in img_files:
            rel_path = str(img.relative_to(base)).replace("\\", "/")
            img_map[rel_path] = img
            img_map[img.name] = img

        out_zip_bytes = io.BytesIO()
        with zipfile.ZipFile(out_zip_bytes, "w", zipfile.ZIP_DEFLATED) as outzip:
            for idx, md_file in enumerate(md_files, 1):
                with open(md_file, "r", encoding="utf-8") as f:
                    md_text = f.read()
                bucket = utils.get_bucket()
                replacements = []
                log = []
                for match, img_path in utils.iter_local_images(md_text):
                    img_path_norm = img_path.lstrip("./").replace("\\", "/")
                    img_file = img_map.get(img_path) or img_map.get(img_path_norm) or img_map.get(Path(img_path).name)
                    if not img_file:
                        log.append(f"⚠️ 未找到图片: {img_path}")
                        continue
                    with open(img_file, "rb") as imgf:
                        url = utils.upload_image(bucket, imgf.read(), img_file.suffix, prefix)
                    replacements.append((match.span(1), url))
                    log.append(f"✅ {img_path} → {url}")
                for (start, end), url in sorted(replacements, key=lambda x: x[0][0], reverse=True):
                    md_text = md_text[:start] + url + md_text[end:]
                out_name = str(md_file.relative_to(base)).replace(".md", "_oss.md")
                outzip.writestr(out_name, md_text)
                outzip.writestr(out_name + ".log", "\n".join(log))

        out_zip_bytes.seek(0)
        return StreamingResponse(
            out_zip_bytes,
            headers={"Content-Disposition": "attachment; filename=processed_md.zip"},
            media_type="application/zip"
        )
