import requests
import json
import nltk
from telethon import TelegramClient, events
from collections import deque
import asyncio
import time

# Remember to use your own values from my.telegram.org!
api_id = 1025907
api_hash = '452b0359b988148995f22ff0f4229750'
proxy_port = 1081
client = TelegramClient('anon', api_id, api_hash,
                        proxy=("socks5", '127.0.0.1', proxy_port))

print("downloading nltk data")
# 下载必要的NLTK数据
nltk.download('vader_lexicon')
print("downloading nltk data done")

# 设置OpenAI API密钥（**请确保妥善管理您的API密钥**）
OPENAI_API_KEY = "sk-9JABKD0bYBgwUV9EJgoHl7GTmPViqpDun338BKJD0d7GWP1w"  # 替换为您的实际API密钥

# 定义一个函数，用于向 AI 发送消息并处理响应


def send_message_to_ai(message_content):
    response = requests.post(
        url="https://api.red-pill.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": "gpt-4",  # 使用适当的模型
            "messages": [
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            "max_tokens": 150,  # 限制回复长度，确保不超过两句话
            "temperature": 0.7,  # 控制回复的创造性
            "n": 1,  # 每次生成一个回复
            "stop": None  # 可以根据需要设置停止词
        })
    )

    # 返回响应的状态和内容
    return response.status_code, response.json()

# 判断文本是否包含中文字符


def is_chinese(text):
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

# 获取汇总消息中的最后一条消息


def get_last_message(messages_summary):
    messages = [msg.strip()
                for msg in messages_summary.strip().split('\n') if msg.strip()]
    if messages:
        return messages[-1]
    return ""

# 生成提示的函数，根据最后一条消息的语言生成相应的提示


def generate_prompt(messages_summary):
    last_message = get_last_message(messages_summary)

    if not last_message:
        # 如果没有消息，生成一个通用的提示
        prompt = (
            "你是群组中的一员，和大家一样关心加密货币。"
            "请根据群组内的讨论生成简短、有趣的回应，不超过两句话。"
            "避免使用固定的开头词，保持语言的灵活性和多样性。"
            "你的评论："
        )
        return prompt

    # 判断最后一条消息的语言
    if is_chinese(last_message):
        # 中文提示
        prompt = (
            "你是群组中的一员，和大家一样关心加密货币。"
            "群组成员们最近在讨论加密货币的价格波动、投资亏损等话题。"
            "在这样的讨论中，你会以友善、稳重的语气进行回应，"
            "通过暗示或陈述的方式表达你的观点，避免指导和教导。"
            "你不用提到群友的名字，只需要根据群友们的消息生成一个自然、简洁的评论，不超过两句话。\n\n"
            "群友消息：\n\n"
            f"群友消息：{messages_summary}\n\n"
            "你的评论："
        )
    else:
        # 英文提示
        prompt = (
            "You are a member of the group, equally interested in cryptocurrencies as everyone else. "
            "Recently, group members have been discussing cryptocurrency price fluctuations, investment losses, and other related topics. "
            "In these discussions, you respond with a friendly and steady tone, using hints or statements to express your views without giving directives or instructions. "
            "You don't need to mention group members' names, just generate a natural and concise comment based on their messages, not exceeding two sentences.\n\n"            "Group messages:\n\n"
            f"Group messages:{messages_summary}\n\n"
            "Your comment:"
        )

    return prompt


def generate_comment(messages_summary):
    try:
        # 生成提示
        prompt = generate_prompt(messages_summary)

        # 调用 AI API
        status_code, response_content = send_message_to_ai(prompt)

        if status_code == 200:
            # 获取AI回复
            ai_response = response_content['choices'][0]['message']['content'].strip(
            )
            return ai_response

    except Exception as e:
        print(e)
        return ""


# Add these variables before the event handler
message_buffer = deque(maxlen=10)  # Stores last 10 messages
last_reply_time = 0
REPLY_INTERVAL = 5  # 5 seconds interval


@client.on(events.NewMessage)
async def my_event_handler(event):
    global last_reply_time
    sender = await event.get_sender()
    chat_id = event.chat_id

    if chat_id == -4619464166:
        msg = f"{sender.first_name} {sender.last_name}: {event.raw_text}"
        # Record the message
        message_buffer.append(msg)
        print(msg)
        print()

        # Check if enough time has passed since last reply
        current_time = time.time()
        if current_time - last_reply_time >= REPLY_INTERVAL:
            # Combine recent messages for context
            messages_summary = "\n".join(list(message_buffer))
            reply = generate_comment(messages_summary)
            await event.respond(reply)
            last_reply_time = current_time
            # Clear the message buffer after sending response
            message_buffer.clear()

client.start()
client.run_until_disconnected()
