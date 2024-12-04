import gradio as gr
import subprocess
import os
from PIL import Image
import numpy as np

# 确保上传目录存在
os.makedirs("/data/uploads", exist_ok=True)

def save_image(image):
    """保存图片并返回路径"""
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    path = "/data/uploads/temp.png"
    image.save(path)
    return path

def run_ocr(image, ocr_type="ocr", box=None, color=None, render=False):
    """运行OCR命令并返回结果"""
    try:
        # 保存图片
        image_path = save_image(image)
        
        # 构建基本命令
        cmd = [
            "python3", "/app/GOT/demo/run_ocr_2.0.py",
            "--model-name", "/app/GOT_weights",
            "--image-file", image_path,
            "--type", ocr_type
        ]
        
        # 添加可选参数
        if box:
            cmd.extend(["--box", box])
        if color:
            cmd.extend(["--color", color])
        if render:
            cmd.append("--render")
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 清理临时文件
        os.remove(image_path)
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"错误: {result.stderr}"
            
    except Exception as e:
        return f"发生错误: {str(e)}"

def process_image(image, ocr_type, box_input, color_choice, render):
    """处理图片的主函数"""
    if image is None:
        return "请上传图片"
    
    # 处理box参数
    box = None
    if box_input:
        try:
            # 将输入转换为box格式
            coords = [int(x.strip()) for x in box_input.split(',')]
            if len(coords) == 4:
                box = f"[{','.join(map(str, coords))}]"
            else:
                return "Box格式错误: 需要4个数字 (x1,y1,x2,y2)"
        except ValueError:
            return "Box格式错误: 请输入有效的数字"
    
    # 运行OCR
    result = run_ocr(
        image=image,
        ocr_type=ocr_type,
        box=box,
        color=color_choice if color_choice != "none" else None,
        render=render
    )
    
    return result

# 创建Gradio界面
with gr.Blocks(title="GOT-OCR 2.0", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # GOT-OCR 2.0 演示
    
    这是一个通用OCR系统，支持多种识别模式和功能。
    
    ### 功能特点:
    - 支持普通OCR和格式化输出
    - 支持区域识别
    - 支持颜色识别
    - 支持结果渲染
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            # 输入部分
            input_image = gr.Image(
                tools=["select"],
                type="pil",
                label="上传图片"
            )
            
            with gr.Row():
                ocr_type = gr.Radio(
                    choices=["ocr", "format"],
                    value="ocr",
                    label="识别模式"
                )
                color_choice = gr.Radio(
                    choices=["none", "red", "green", "blue"],
                    value="none",
                    label="颜色选择"
                )
            
            box_input = gr.Textbox(
                label="区域选择 (可选, 格式: x1,y1,x2,y2)",
                placeholder="例如: 100,100,500,500"
            )
            
            render_checkbox = gr.Checkbox(
                label="渲染结果",
                value=False
            )
            
            submit_btn = gr.Button("开始识别", variant="primary")
        
        with gr.Column(scale=1):
            # 输出部分
            output_text = gr.Textbox(
                label="识别结果",
                lines=10,
                show_copy_button=True
            )
    
    # 添加示例
    gr.Examples(
        examples=[
            ["example1.png", "ocr", "", "none", False],
            ["example2.png", "format", "", "none", True],
        ],
        inputs=[input_image, ocr_type, box_input, color_choice, render_checkbox],
        outputs=output_text,
        fn=process_image,
        cache_examples=True,
    )
    
    # 设置提交动作
    submit_btn.click(
        fn=process_image,
        inputs=[input_image, ocr_type, box_input, color_choice, render_checkbox],
        outputs=output_text
    )
    
    # 添加使用说明
    gr.Markdown("""
    ### 使用说明
    
    1. **上传图片**: 支持常见图片格式(PNG, JPG等)
    2. **选择模式**: 
       - OCR: 普通文字识别
       - Format: 格式化输出
    3. **颜色选择**: 可选择特定颜色的文字进行识别
    4. **区域选择**: 可输入坐标来识别特定区域
    5. **渲染结果**: 对于格式化输出，可选择是否渲染结果
    
    ### 注意事项
    
    - 区域选择格式为: x1,y1,x2,y2 (左上角和右下角坐标)
    - 建议图片分辨率不要太大，以获得最佳识别效果
    - 格式化输出模式下建议开启渲染以获得更好的可视化效果
    """)

# 启动服务
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    ) 