import os
import requests
from dotenv import load_dotenv
import json
import time

# 加载环境变量
load_dotenv('key.env')
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    print("错误：请在 key.env 文件中设置 DEEPSEEK_API_KEY")
    exit(1)

def get_completion_from_messages(messages, model="deepseek-chat", temperature=0.7):
    """
    获取 DeepSeek 模型的完成响应（多条消息）
    
    参数:
    messages -- 消息列表，格式为 [{"role": "user", "content": "..."}, ...]
    model -- DeepSeek 模型名称 (默认: "deepseek-chat")
    temperature -- 生成结果的随机性 (0-1, 默认: 0.7)
    
    返回:
    模型生成的文本内容
    """
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(
            url, 
            data=json.dumps(data, ensure_ascii=False),
            headers=headers,
            timeout=30  # 设置超时时间
        )
        response.raise_for_status()
        result = response.json()
        
        # 返回模型生成的文本内容
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"API请求出错: {e}")
        return None

class BaoziOrderAssistant:
    def __init__(self):
        # 初始化上下文
        self.context = [
            {
                "role": "system",
                "content": (
                    "你是包子店的点餐助手小陈同学，负责帮助顾客完成点餐。"
                    "包子店有以下产品：\n"
                    "1. 鲜肉包 - 3元/个\n"
                    "2. 豆沙包 - 2.5元/个\n"
                    "3. 青菜包 - 2元/个\n"
                    "4. 奶黄包 - 3.5元/个\n"
                    "5. 三鲜包 - 4元/个\n"
                    "6. 牛肉包 - 5元/个\n\n"
                    "点餐流程：\n"
                    "1. 热情欢迎顾客\n"
                    "2. 询问顾客需要的包子种类和数量\n"
                    "3. 确认订单\n"
                    "4. 询问是否需要其他帮助\n"
                    "5. 礼貌告别\n\n"
                    "每次只问一个问题，保持对话简洁友好。"
                )
            }
        ]
        
        # 当前订单信息
        self.order = {
            "items": [],
            "total_price": 0.0,
            "completed": False
        }
        
        # 包子价格表
        self.menu = {
            "鲜肉包": 3.0,
            "豆沙包": 2.5,
            "青菜包": 2.0,
            "奶黄包": 3.5,
            "三鲜包": 4.0,
            "牛肉包": 5.0
        }
    
    def add_to_context(self, role, content):
        """将消息添加到上下文"""
        self.context.append({"role": role, "content": content})
    
    def process_order(self, user_input):
        """处理用户输入并更新订单"""
        # 将用户输入添加到上下文
        self.add_to_context("user", user_input)
        
        # 获取助手回复
        assistant_reply = get_completion_from_messages(self.context)
        
        if not assistant_reply:
            assistant_reply = "抱歉，我遇到了点问题，请稍后再试。"
        
        # 将助手回复添加到上下文
        self.add_to_context("assistant", assistant_reply)
        
        # 解析订单信息
        self._parse_order(assistant_reply)
        
        return assistant_reply
    
    def _parse_order(self, text):
        """从对话中解析订单信息"""
        # 检查是否完成订单
        if "订单完成" in text or "感谢" in text:
            self.order["completed"] = True
        
        # 提取订单项目
        lines = text.split('\n')
        for line in lines:
            if "：" in line and "个" in line:
                parts = line.split('：')
                if len(parts) > 1:
                    item_part = parts[0].strip()
                    quantity_part = parts[1].split('个')[0].strip()
                    
                    # 查找匹配的包子类型
                    for baozi in self.menu:
                        if baozi in item_part:
                            try:
                                quantity = int(quantity_part)
                                price = self.menu[baozi] * quantity
                                
                                # 添加到订单
                                self.order["items"].append({
                                    "name": baozi,
                                    "quantity": quantity,
                                    "price": price
                                })
                                
                                # 更新总价
                                self.order["total_price"] += price
                            except ValueError:
                                pass
    
    def generate_order_summary(self):
        """生成订单摘要"""
        if not self.order["items"]:
            return "暂无订单信息"
        
        summary = "【订单摘要】\n"
        for item in self.order["items"]:
            summary += f"{item['name']}: {item['quantity']}个, {item['price']}元\n"
        
        summary += f"\n总计: {self.order['total_price']}元"
        return summary
    
    def reset_order(self):
        """重置订单和上下文"""
        self.context = self.context[:1]  # 保留系统消息
        self.order = {
            "items": [],
            "total_price": 0.0,
            "completed": False
        }

def display_welcome():
    """显示欢迎界面"""
    print("=" * 50)
    print("欢迎使用小陈同学包子点餐系统")
    print("=" * 50)
    print("本系统由DeepSeek AI驱动")
    print("输入 '退出' 结束点餐")
    print("输入 '重置' 重新开始点餐")
    print("输入 '订单' 查看当前订单")
    print("=" * 50)
    print("\n小陈同学正在等待为您服务...\n")

def run_chat_interface():
    """运行聊天界面"""
    assistant = BaoziOrderAssistant()
    display_welcome()
    
    # 初始问候
    initial_greeting = assistant.process_order("你好")
    print(f"小陈同学: {initial_greeting}")
    
    while True:
        user_input = input("您: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() in ["退出", "exit", "quit"]:
            print("\n小陈同学: 感谢光临，期待下次为您服务！")
            break
            
        if user_input == "重置":
            assistant.reset_order()
            print("\n小陈同学: 已重置订单，我们可以重新开始点餐！")
            continue
            
        if user_input == "订单":
            summary = assistant.generate_order_summary()
            print(f"\n{summary}\n")
            continue
            
        # 处理用户输入
        response = assistant.process_order(user_input)
        
        # 显示助手回复
        print(f"\n小陈同学: {response}")
        
        # 添加一点延迟，使对话更自然
        time.sleep(0.5)
        
        # 如果订单完成，询问是否继续
        if assistant.order["completed"]:
            choice = input("\n是否开始新订单? (是/否): ").strip().lower()
            if choice in ["是", "yes", "y"]:
                assistant.reset_order()
                print("\n小陈同学: 已开始新订单，请问您需要什么？")
            else:
                print("\n小陈同学: 感谢光临，再见！")
                break

if __name__ == "__main__":
    run_chat_interface()