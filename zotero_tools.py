from pyzotero import zotero
import os
from openai import OpenAI
import pdfplumber
from typing import Optional, Dict, Any
import time
import yaml

def load_config() -> Dict[str, Any]:
    """加载配置文件，优先读取开发配置文件"""
    config_files = ['zotero_config_dev.yaml', 'zotero_config.yaml']
    
    for config_file in config_files:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                print(f"使用配置文件: {config_file}")
                return config
    
    raise FileNotFoundError("未找到配置文件")

# 加载配置
config = load_config()
zotero_config = config['zotero']
openai_config = config['openai']

# 初始化客户端
openai_client = OpenAI(
    api_key=openai_config['api_key'],
    base_url=openai_config.get('base_url')  # 使用 get 方法处理可选参数
)

zot = zotero.Zotero(
    str(zotero_config['user_id']), 
    'user', 
    zotero_config['api_key']
)

userprofile = os.path.expanduser('~')
local_storage = os.path.join(userprofile, 'Zotero', 'storage')


def extract_pdf_text(pdf_path: str) -> str:
    """从PDF文件中提取文本"""
    text = ""
    try:
        print(f"\n正在读取PDF文件: {os.path.basename(pdf_path)}")
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"PDF处理错误: {e}")
        return ""
    return text

def generate_summary(text: str) -> str:
    """使用LLM生成文本摘要，支持流式输出"""
    try:
        print("\n正在生成摘要...\n")
        response = openai_client.chat.completions.create(
            model=openai_config['model'],
            messages=[
                {
                    "role": "system",
                    "content": openai_config.get('prompt', "你是一个资深的学者，擅长用专业而简洁的语言为用户总结学术论文内容。")
                },
                {"role": "user", "content": f"请总结以下学术论文内容：\n{text}"}
            ],
            temperature=0.7,
            stream=True  # 启用流式输出
        )
        
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end='', flush=True)
                full_response += content
        print("\n")  # 完成后换行
        return full_response
    except Exception as e:
        print(f"LLM处理错误: {e}")
        return ""

def check_note_with_ai_summary(item_key: str) -> bool:
    """检查item是否有带有指定标签的笔记"""
    children = zot.children(item_key)
    for child in children:
        if child['data']['itemType'] == 'note':
            if any(tag['tag'] == zotero_config['summary_tag'] for tag in child['data'].get('tags', [])):
                return True
    return False

def has_ai_summary_tag(item: Dict[str, Any]) -> bool:
    """检查item是否已有指定标签的笔记"""
    return check_note_with_ai_summary(item['key'])

def process_collection(collection_key: str):
    """处理指定collection中的所有项目"""
    items = zot.collection_items_top(collection_key)
    
    for item in items:
        # 跳过已有指定标签的笔记的项目
        if has_ai_summary_tag(item):
            print(f"跳过已有{zotero_config['summary_tag']}标签的笔记: {item['data'].get('title', '未知标题')}")
            continue
            
        print(f"\n处理文献: {item['data'].get('title', '未知标题')}")
        
        # 获取附件
        attachments = zot.children(item['key'])
        pdf_path = None
        
        # 查找PDF附件
        for attachment in attachments:
            if (attachment['data']['itemType'] == 'attachment' and 
                attachment['data'].get('contentType') == 'application/pdf'):
                pdf_path = os.path.join(local_storage, attachment['data']['key'], 
                                      attachment['data']['filename'])
                break
        
        if pdf_path and os.path.exists(pdf_path):
            # 提取PDF文本
            text = extract_pdf_text(pdf_path)
            if text:
                # 生成摘要
                summary = generate_summary(text)
                if summary:
                    # 创建新笔记
                    template = f'<div data-schema-version="9"><p>{summary}</p></div>'
                    
                    # 添加带标签的笔记
                    zot.create_items([{
                        'itemType': 'note',
                        'parentItem': item['key'],
                        'note': template,
                        'tags': [{'tag': zotero_config['summary_tag']}]
                    }])
                    
                    print(f"已为文献 {item['data'].get('title', '未知标题')} 添加AI摘要")
                    time.sleep(1)  # 避免API限制

if __name__ == "__main__":
    # 获取所有collections
    collections = zot.collections()
    
    # 打印collections供用户选择
    print("请选择要处理的collection:")
    for i, collection in enumerate(collections):
        print(f"{i+1}. {collection['data']['name']}")
        
    # 获取用户输入
    while True:
        try:
            choice = int(input("请输入序号: ")) - 1
            if 0 <= choice < len(collections):
                break
            print("无效的序号,请重新输入")
        except ValueError:
            print("请输入数字")
    
    # 处理选中的collection
    collection_key = collections[choice]['key']
    process_collection(collection_key)

