import os
import time
import psutil
import aiohttp
import qqbot
from qqbot.core.util.yaml_util import YamlUtil
import re
import logging
import multiprocessing

# 设置日志配置
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 控制台输出日志
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# 文件输出日志
file_handler = logging.FileHandler('robot.log', mode='a', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# 从配置文件读取机器人的信息
test_config = YamlUtil.read(os.path.join(os.path.dirname(__file__), "config.yaml"))

API_KEY = test_config["amap"].get("api_key")  # 获取API_KEY
if not API_KEY:
    logger.error("API_KEY未配置，请检查config.yaml文件。")
    raise ValueError("API_KEY未配置")

WEATHER_API_URL = "https://restapi.amap.com/v3/weather/weatherInfo"

# 状态变量
is_running = True
t_token = qqbot.Token(test_config["token"]["appid"], test_config["token"]["token"])

# 记录程序开始时间
start_time = time.time()

async def get_weather(city):
    params = {
        'city': city,
        'key': API_KEY,
        'output': 'JSON'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(WEATHER_API_URL, params=params) as response:
                response.raise_for_status()  # 检查请求状态
                data = await response.json()
                if data.get('status') == "1":
                    weather_info = data['lives'][0]
                    weather_description = weather_info['weather']
                    temperature = weather_info['temperature']
                    return f"{city}的天气是：{weather_description}，温度为 {temperature} °C"
                else:
                    return "天气信息获取失败，请检查城市名称或API配置。"
    except aiohttp.ClientError as e:
        logger.error(f"获取天气信息时发生网络错误：{e}")
        return "获取天气信息时发生网络错误，请稍后再试。"
    except Exception as e:
        logger.error(f"获取天气信息时发生错误：{e}")
        return f"天气信息获取出现错误：{e}"

def get_system_status():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        total_memory = memory_info.total / (1024 * 1024)
        used_memory = memory_info.used / (1024 * 1024)
        memory_usage = (used_memory / total_memory) * 100

        disk_info = psutil.disk_usage('/')
        total_disk = disk_info.total / (1024 * 1024 * 1024)
        used_disk = disk_info.used / (1024 * 1024 * 1024)
        disk_usage = (used_disk / total_disk) * 100
        
        runtime = time.time() - start_time
        return cpu_usage, memory_usage, disk_usage, runtime
    except Exception as e:
        logger.error(f"获取系统状态时发生错误：{e}")
        return None, None, None, None

async def _message_handler(event, message: qqbot.Message):
    msg_api = qqbot.AsyncMessageAPI(t_token, False)
    
    # 处理消息内容，去掉@用户部分
    content = re.sub(r'<@!?\d+>', '', message.content).strip()
    logger.info(f"收到消息：{content}")  # 记录收到的消息
    
    # 去掉前缀 /
    if content.startswith("/"):
        content = content[1:].strip()

    global is_running
    if content == "运行状态":
        cpu_usage, memory_usage, disk_usage, runtime = get_system_status()
        if cpu_usage is not None:  # 确保状态正常
            reply_content = (
                f"当前状态：运行中\n"
                f"CPU占用：{cpu_usage}%\n"
                f"内存占用：{memory_usage:.2f}%\n"
                f"存储占用：{disk_usage:.2f}%\n"
                f"总运行时间：{runtime:.2f} 秒"
            )
            logger.info("回复运行状态请求")  # 记录发送状态回复的信息
        else:
            reply_content = "获取系统状态时发生错误。"
    elif content.startswith("天气"):
        city = content[len("天气"):].strip()
        if city:
            reply_content = await get_weather(city)
            logger.info(f"回复天气请求：{reply_content}")  # 记录天气请求的回复信息
        else:
            reply_content = "格式不正确，请使用：天气 <城市名>"
            logger.warning(f"天气请求格式不正确：{content}")  # 记录警告日志
    else:
        reply_content = "我不太明白你说的是什么..."
        logger.warning(f"无法理解的请求：{content}")  # 记录无法理解的请求

    # 回复消息
    message_to_send = qqbot.MessageSendRequest(content=reply_content, msg_id=message.id)
    await msg_api.post_message(message.channel_id, message_to_send)

def run_bot():
    """运行机器人，作为守护进程"""
    logger.info("机器人启动中...")
    qqbot_handler = qqbot.Handler(qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _message_handler)
    qqbot.async_listen_events(t_token, False, qqbot_handler)

if __name__ == "__main__":
    # 创建并启动守护进程
    bot_process = multiprocessing.Process(target=run_bot)
    bot_process.daemon = True  # 设置为守护进程
    bot_process.start()

    try:
        while True:
            time.sleep(1)  # 维持主程序的运行
    except KeyboardInterrupt:
        logger.info("程序被手动终止。")
