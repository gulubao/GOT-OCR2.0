from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import subprocess
import os
import shutil
from typing import Optional, List
import uvicorn
from pydantic import BaseModel

app = FastAPI(title="GOT-OCR API", description="GOT-OCR2.0 REST API服务")

# 确保上传目录存在
os.makedirs("/data/uploads", exist_ok=True)

class OCRResponse(BaseModel):
    """OCR响应模型"""
    success: bool
    result: str
    error: Optional[str] = None

@app.post("/ocr", response_model=OCRResponse)
async def ocr_endpoint(
    file: UploadFile = File(...),
    ocr_type: str = Form("ocr"),  # ocr 或 format
    box: Optional[str] = Form(None),  # 格式: "x1,y1,x2,y2"
    color: Optional[str] = Form(None),  # 指颜色识别 (red/green/blue)
    render: bool = Form(False)
):
    """
    OCR识别接口
    
    参数:
    - file: 图片文件
    - ocr_type: 识别类型 (ocr/format)
    - box: 指定区域识别 [x1,y1,x2,y2]
    - color: 指颜色识别 (red/green/blue)
    - render: 是否渲染格式化结果
    """
    try:
        # 保存上传的文件
        file_path = f"/data/uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 构建OCR命令
        cmd = ["python3", "/app/GOT/demo/run_ocr_2.0.py", 
               "--model-name", "/app/GOT_weights",
               "--image-file", file_path,
               "--type", ocr_type]
        
        # 添加可选参数
        if box:
            cmd.extend(["--box", box])
        if color:
            cmd.extend(["--color", color])
        if render:
            cmd.append("--render")
        
        # 执行OCR命令
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True)
        
        # 删除临时文件
        os.remove(file_path)
        
        if result.returncode == 0:
            return OCRResponse(
                success=True,
                result=result.stdout
            )
        else:
            return OCRResponse(
                success=False,
                result="",
                error=result.stderr
            )
            
    except Exception as e:
        return OCRResponse(
            success=False,
            result="",
            error=str(e)
        )

@app.post("/batch-ocr", response_model=OCRResponse)
async def batch_ocr_endpoint(
    files: List[UploadFile] = File(...),
    ocr_type: str = Form("ocr")
):
    """
    批量OCR识别接口
    
    参数:
    - files: 多个图片文件
    - ocr_type: 识别类型 (ocr/format)
    """
    try:
        # 创建临时目录
        batch_dir = "/data/uploads/batch"
        os.makedirs(batch_dir, exist_ok=True)
        
        # 保存所有文件
        for file in files:
            file_path = os.path.join(batch_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        
        # 执行批量OCR
        cmd = ["python3", "/app/GOT/demo/run_ocr_2.0.py",
               "--model-name", "/app/GOT_weights",
               "--image-file", batch_dir,
               "--type", ocr_type,
               "--multi-page"]
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True)
        
        # 清理临时文件
        shutil.rmtree(batch_dir)
        
        if result.returncode == 0:
            return OCRResponse(
                success=True,
                result=result.stdout
            )
        else:
            return OCRResponse(
                success=False,
                result="",
                error=result.stderr
            )
            
    except Exception as e:
        return OCRResponse(
            success=False,
            result="",
            error=str(e)
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 