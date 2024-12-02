import asyncio
import os
from typing import Optional, List
from pathlib import Path
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Bot, Message
from nonebot_plugin_alconna import Alconna, on_alconna
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import httpx
from io import BytesIO
from datetime import datetime
import asyncio
from .QuoteScene import render_quote_scene

FONT_PATH = Path("YaHei Consolas Hybrid 1.12.ttf")
SUB_FONT_PATH = Path("YaHei Consolas Hybrid 1.12.ttf")

cmd = Alconna(".q")
command = on_alconna(cmd, aliases={"q"})


@command.handle()
async def handle_command(bot: Bot, event: MessageEvent):
    if not event.reply:
        await command.send(MessageSegment.text("请回复一条消息以使用此命令。"))
        return

    reply_content = extract_reply_content(event.reply.message)
    user_id = event.reply.sender.user_id
    nickname = event.reply.sender.nickname
    if user_id == event.self_id:
        await command.send(MessageSegment.text("Σ( ° △ °|||)︴\n不能回复咱自己的信息"))
        return

    now_strftime = datetime.now().strftime('%Y%m%d-%H%M%S')

    avatar_url = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    avatar_image = await fetch_image_from_url(avatar_url)
    await save_image(
        image=avatar_image,
        save_path='./tmp/image/avatar/',
        file_name='avatar_{}_{}.png'.format(nickname, now_strftime)
    )

    if avatar_image is None:
        await command.send(MessageSegment.text("无法获取用户头像，请检查网络连接。"))
        return
    additional_image = None
    image_segment = next((seg for seg in event.reply.message if seg.type == "image"), None)
    if image_segment:
        image_url = image_segment.data['url']
        additional_image = await fetch_image_from_url(image_url)
        await save_image(
            image=additional_image,
            save_path='./tmp/image/additional/',
            file_name='additional_{}_{}.png'.format(nickname, now_strftime)
        )

    # result_image = await process_image(avatar_image_path, reply_content, nickname, additional_image)
    result_image_path = await async_render_quote_image(
        output_filename="result_{}_{}.png".format(nickname, now_strftime),
        avatar_image_path='./tmp/image/avatar/avatar_{}_{}.png'.format(nickname, now_strftime),
        quote_text=reply_content,
        nickname_text=nickname,
        additional_image_path='./tmp/image/additional/additional_{}_{}.png'.format(nickname, now_strftime),
        font_path=""
    )

    result_image = await load_image(result_image_path)

    if result_image is not None:
        image_bytes = BytesIO()
        result_image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        await command.send(MessageSegment.image(image_bytes))
    else:
        await command.send(MessageSegment.text("处理图片时发生错误，请检查输入参数。"))


def extract_reply_content(reply_msg: Message) -> str:
    reply_content = ""
    for segment in reply_msg:
        if segment.type == "text":
            reply_content += segment.data['text']
    return reply_content.strip()


async def fetch_image_from_url(url: str) -> Optional[Image.Image]:
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            image_data = response.content
            return Image.open(BytesIO(image_data))
        except httpx.RequestError as e:
            logger.warning(f"Failed to fetch image from {url}: {e}")
            return None


async def save_image(image: Image.Image, save_path: str, file_name: str) -> str:
    """
    Save the fetched image to the specified location 然后返回绝对路径.
    
    :param image: The PIL Image object to save.
    :param save_path: The directory path where the image will be saved.
    :param file_name: 文件名包含扩展后缀 to save the image as.
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)  # Create the directory if it doesn't exist
    file_path = os.path.join(save_path, file_name)

    try:
        image.save(file_path)  # Save the image
        print(f"Image saved to {file_path}")
    except Exception as e:
        print(f"Failed to save image: {e}")


# async def process_image(avatar_image: str,
#                         quote_text: str,
#                         nickname: str,
#                         additional_image_path: str) -> str:
#     loop = asyncio.get_event_loop()
#
#     def _process():
#         pass
#
#     return await loop.run_in_executor(None, _process)


async def async_render_quote_image(
        # now_strftime: str,
        output_filename: str,
        avatar_image_path: str,
        quote_text: str,
        nickname_text: str,
        additional_image_path: str,
        font_path: str = "",
        output_format: str = "png"
) -> str:
    loop = asyncio.get_event_loop()

    def _process():
        # 这里调用你的同步渲染函数
        return render_quote_scene(
            output_filename=output_filename,
            avatar_image_path=avatar_image_path,
            quote_text=quote_text,
            nickname_text=nickname_text,
            additional_image_path=additional_image_path,
            font_path=font_path,
            output_format=output_format
        )
        # 返回生成的文件路径（假设渲染后文件保存在当前目录下）
        # return "./tmp/result/result_{}_{}".format(nickname_text, now_strftime)

    # 使用 run_in_executor 在单独的线程中运行同步函数
    result = await loop.run_in_executor(None, _process)
    return result


async def load_image(image_path: str) -> Image.Image:
    """
    从给定的路径加载图片，并返回一个Image.Image对象。

    :param image_path: 图片文件的路径
    :return: Image.Image 对象
    """
    loop = asyncio.get_event_loop()

    def _process():

        try:
            # 使用Image.open()打开图片文件
            img = Image.open(image_path)
            # 确保图片被完全加载到内存中
            img.load()
            return img
        except IOError as e:
            print(f"无法打开图片文件 {image_path}: {e}")
            return None

    return await loop.run_in_executor(None, _process)
