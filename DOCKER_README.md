# GOT-OCR2.0 Docker部署指南

## 前置要求

- Docker
- NVIDIA Container Toolkit
- NVIDIA GPU驱动
- Docker Compose

## 目录结构

```
.
├── Dockerfile          # Docker镜像构建文件
├── docker-compose.yml  # Docker Compose配置文件
├── api_server.py      # API服务器
├── gradio_app.py      # Gradio Web界面
├── data/              # 输入图片目录
└── GOT_weights/       # 模型权重目录(可选)
```

## 快速开始

1. 创建必要的目录:
```bash
mkdir -p data GOT_weights
```

2. 将需要识别的图片放入data目录:
```bash
cp your_image.png data/input.png
```

TODO: dockerfile and dockercompose

## 使用说明

### Web界面模式

访问 http://localhost:7860 即可使用直观的Web界面，支持：

1. 拖拽上传图片
2. 选择OCR模式（普通/格式化）
3. 选择特定颜色识别
4. 指定识别区域
5. 渲染格式化结果
6. 复制识别结果
7. 查看示例

## Demo

```Shell
cd /app/GOT-OCR-2.0-master
```

1. plain texts OCR:
```Shell
python3 GOT/demo/run_ocr_2.0.py  --model-name  /GOT_weights/  --image-file  /an/image/file.png  --type ocr
```
2. format texts OCR:
```Shell
python3 GOT/demo/run_ocr_2.0.py  --model-name  /app/GOT_weights/  --image-file  /an/image/file.png  --type format
python3 GOT/demo/run_ocr_2.0.py  --model-name  /app/GOT_weights/  --image-file  /data/Snipaste_2024-12-04_10-57-08.png  --type format

```
3. fine-grained OCR:
```Shell
python3 GOT-OCR-2.0-master/GOT/demo/run_ocr_2.0.py  --model-name  /GOT_weights/  --image-file  /an/image/file.png  --type format/ocr --box [x1,y1,x2,y2]
```
```Shell
python3 GOT-OCR-2.0-master/GOT/demo/run_ocr_2.0.py  --model-name  /GOT_weights/  --image-file  /an/image/file.png  --type format/ocr --color red/green/blue
```
4. multi-crop OCR:
```Shell
python3 GOT-OCR-2.0-master/GOT/demo/run_ocr_2.0_crop.py  --model-name  /GOT_weights/ --image-file  /an/image/file.png 
```
5. **Note**: This feature is not batch inference!! It works on the token level.  Please read the paper and then correct use multi-page OCR (the image path contains multiple .png files):
```Shell
python3 GOT-OCR-2.0-master/GOT/demo/run_ocr_2.0_crop.py  --model-name  /GOT_weights/ --image-file  /images/path/  --multi-page
```
6. render the formatted OCR results:
```Shell
python3 GOT-OCR-2.0-master/GOT/demo/run_ocr_2.0.py  --model-name  /GOT_weights/  --image-file  /an/image/file.png  --type format --render
 ```
**Note**:
The rendering results can be found in /results/demo.html. Please open the demo.html to see the results.

### 命令行模式

在容器内使用预设的`ocr`命令别名进行OCR识别:
```bash
# 普通OCR识别
ocr --image-file /data/input.png --type ocr

# 格式化输出
ocr --image-file /data/input.png --type format
```

### API模式

API服务器运行在8000端口,提供以下接口:

#### 1. 单图片OCR
```bash
curl -X POST "http://localhost:8000/ocr" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.png" \
  -F "ocr_type=ocr"
```

可选参数:
- ocr_type: ocr(默认)或format
- box: 指定区域,格式"x1,y1,x2,y2"
- color: 指定颜色(red/green/blue)
- render: true/false

#### 2. 批量OCR
```bash
curl -X POST "http://localhost:8000/batch-ocr" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@image1.png" \
  -F "files=@image2.png" \
  -F "ocr_type=ocr"
```

### API响应格式
```json
{
  "success": true,
  "result": "识别结果",
  "error": null
}
```

### 可用参数

- `--type`: 识别类型 (ocr/format)
- `--image-file`: 输入图片路径
- `--box`: 指定区域识别 [x1,y1,x2,y2]
- `--color`: 指定颜色识别 (red/green/blue)
- `--render`: 渲染格式化结果

## 手动安装步骤

如果自动构建失败，可以按照以下步骤手动安装：

### 1. 拉取基础镜像并创建容器

```bash
# 拉取NVIDIA基础镜像
docker pull nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# 创建并启动容器: Linux/Mac
docker run -it --gpus all \
    -p 8000:8000 -p 7860:7860 \
    -v $(pwd)/data:/data \
    -v $(pwd)/GOT_weights:/app/GOT_weights \
    --name got-ocr \
    nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04 bash

# Windows PowerShell
docker run -it --gpus all `
    -p 8000:8000 -p 7860:7860 `
    -v ${PWD}/data:/data `
    -v ${PWD}/GOT_weights:/app/GOT_weights `
    --name got-ocr `
    nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04 bash
```

### 2. 在容器内安装系统依赖

```bash
# 设置时区（避免交互）
export DEBIAN_FRONTEND=noninteractive
export TZ=America/New_York

# 更新并安装依赖
apt-get update && apt-get install -y \
    git \
    python3.10 \
    python3-pip \
    ninja-build \
    tzdata

# 设置时区
ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
dpkg-reconfigure -f noninteractive tzdata

# 清理缓存
rm -rf /var/lib/apt/lists/*
```

### 3. 克隆项目并设置工作目录

```bash
# 创建工作目录
mkdir -p /app && cd /app

# 克隆项目
git clone https://github.com/gulubao/GOT-OCR2.0.git temp
mv temp/* temp/.[!.]* . 2>/dev/null || true
rm -rf temp
```

### 4. 安装Python依赖

```bash
# 升级pip
python3 -m pip install --no-cache-dir --upgrade pip

# 安装PyTorch
pip install --no-cache-dir torch==2.0.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 安装其他依赖
pip install --no-cache-dir packaging
pip install --no-cache-dir ninja
```

```bash
git clone https://github.com/Dao-AILab/flash-attention.git
cd flash-attention
DISABLE_NINJA=1 MAX_JOBS=1 TORCH_CUDA_ARCH_LIST="8.9" python3 setup.py install
cd ..
# rm -rf flash-attention
```

```bash
# MAX_JOBS=2 pip install flash-attn --no-build-isolation # TODO: fail. try compile locally
pip install --no-cache-dir fastapi uvicorn python-multipart
pip install --no-cache-dir gradio>=3.50.2
pip install --no-cache-dir huggingface_hub
pip install --no-cache-dir Pillow numpy
pip install transformers
pip install opencv-python-headless
pip install tiktoken
pip install accelerate
```

### 5. 下载模型权重

```bash
# 创建模型目录
mkdir -p /app/GOT_weights

# 下载模型权重
python3 -c "from huggingface_hub import snapshot_download; snapshot_download('ucaslcl/GOT-OCR2_0', local_dir='/app/GOT_weights')"
```

### 6. 设置便捷命令

```bash
# 添加命令别名
bash
echo 'alias ocr="python3 /app/GOT/demo/run_ocr_2.0.py --model-name /app/GOT_weights"' >> /root/.bashrc
echo 'alias start-api="python3 /app/api_server.py"' >> /root/.bashrc
echo 'alias start-ui="python3 /app/gradio_app.py"' >> /root/.bashrc
source /root/.bashrc
```

### 7. 启动服务

```bash
# 启动Web界面
python3 /app/gradio_app.py
# 或启动API服务
# python3 /app/api_server.py
```

### 8. 保存容器为镜像（可选）

如果你想保存配置好的容器为新的镜像：

```bash
# 在另一个终端中执行（不要在容器内执行）
docker commit got-ocr got-ocr:latest
```

### 9. 后续使用

保存为镜像后，可以直接使用该镜像启动容器：

```bash
docker run -it --gpus all \
  -p 8000:8000 -p 7860:7860 \
  -v $(pwd)/data:/data \
  -v $(pwd)/GOT_weights:/app/GOT_weights \
  got-ocr:latest bash
```

```bash
# Windows PowerShell
docker run -it --gpus all `
    -p 8000:8000 -p 7860:7860 `
    -v ${PWD}/data:/data `
    -v ${PWD}/GOT_weights:/app/GOT_weights `
    --name got-ocr `
    got-ocr:latest bash
```

### 常见问题解决

1. 如果出现 CUDA 相关错误：
   ```bash
   # 检查CUDA可用性
   python3 -c "import torch; print(torch.cuda.is_available())"
   # 检查CUDA版本
   nvidia-smi
   ```

2. 如果出现内存不足：
   ```bash
   # 清理pip缓存
   pip cache purge
   # 清理apt缓存
   apt-get clean
   ```

3. 如果模型下载失败：
   ```bash
   # 可以尝试使用代理或手动下载后复制到容器中
   docker cp ./GOT_weights got-ocr:/app/
   ```

4. 如果依赖安装失败：
   ```bash
   # 可以尝试逐个安装并查看具体错误
   pip install package-name -v
   ```