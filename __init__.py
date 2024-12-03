import asyncio
import os
from typing import Optional, List
from pathlib import Path
from nonebot import logger, require
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Bot, Message
from nonebot_plugin_alconna import Alconna, on_alconna, Match, Option
# from arclet.alconna import Args, Option
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import httpx
from io import BytesIO
from datetime import datetime
import asyncio
from .QuoteScene import render_quote_scene
from .QuoteScene_Tex import render_quote_scene_Tex
from .QuoteScene_Tex_video import render_quote_scene_Tex_video
from manim import *

# cmd = Alconna(".qm")
# command = on_alconna(cmd, aliases={"qm"})
cmd = Alconna(
    ".qm",
    Option("--image"),
    Option("--video")
)
command = on_alconna(cmd, aliases={"qm"})

script_path = os.path.abspath(__file__)
print("abspath = ", script_path)

@command.handle()
async def handle_command(
    bot: Bot, 
    event: MessageEvent,
    image: Optional[Match] = cmd.find("image"),
    video: Optional[Match] = cmd.find("video")
):
    
    if image and image.matched:
        mode_num = 1
    elif video and video.matched:
        mode_num = 2
    else:
        mode_num = 1  # 默认为 image 模式
        
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
    avatar_image_save_dir_path = os.path.join(
        os.path.dirname(script_path),
        'tmp', 'image', 'avatar'
    )
    await save_image(
        image=avatar_image,
        # save_path='./tmp/image/avatar/',
        save_path=avatar_image_save_dir_path,
        file_name='avatar_{}_{}.png'.format(nickname, now_strftime)
    )

    if avatar_image is None:
        await command.send(MessageSegment.text("无法获取用户头像，请检查网络连接。"))
        return
    additional_image = None
    additional_image_save_dir_path = ""
    image_segment = next((seg for seg in event.reply.message if seg.type == "image"), None)
    if image_segment:
        image_url = image_segment.data['url']
        additional_image = await fetch_image_from_url(image_url)
        additional_image_save_dir_path = os.path.join(
            os.path.dirname(script_path),
            'tmp', 'image', 'additional'
        )
        await save_image(
            image=additional_image,
            # save_path='./tmp/image/additional/',
            save_path=additional_image_save_dir_path,
            file_name='additional_{}_{}.png'.format(nickname, now_strftime)
        )
    
    avatar_image_path_with_filename = avatar_image_save_dir_path+'/avatar_{}_{}.png'.format(nickname, now_strftime)
    
    additional_image_path_with_filename = ""
    if additional_image_save_dir_path != "":
        additional_image_path_with_filename = additional_image_save_dir_path+'/additional_{}_{}.png'.format(nickname, now_strftime)

    # result_image = await process_image(avatar_image_path, reply_content, nickname, additional_image)
    result_image_path_with_filename = await async_render_quote_image(
        output_filename="result_{}_{}.png".format(nickname, now_strftime),
        # avatar_image_path='./tmp/image/avatar/avatar_{}_{}.png'.format(nickname, now_strftime),
        avatar_image_path=avatar_image_path_with_filename,
        quote_text=reply_content,
        nickname_text=nickname,
        # additional_image_path='./tmp/image/additional/additional_{}_{}.png'.format(nickname, now_strftime),
        additional_image_path= additional_image_path_with_filename,
        font_path="",
        mode=mode_num
    )

    result_image = await load_image(result_image_path_with_filename)

    if result_image is not None:
        image_bytes = BytesIO()
        result_image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        await command.send(MessageSegment.image(image_bytes))
    else:
        await command.send(MessageSegment.text("处理图片时发生错误，请检查输入参数。"))
        
    delete_image(avatar_image_path_with_filename)
    delete_image(additional_image_path_with_filename)
    delete_image(result_image_path_with_filename)


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
        output_format: str = "png",
        mode: int = 0,
) -> str:
    loop = asyncio.get_event_loop()

    def _process():
        # 这里调用你的同步渲染函数
        flist = [
            render_quote_scene, 
            render_quote_scene_Tex, 
            render_quote_scene_Tex_video
        ]
        f = flist[mode]
        res = f(
            output_filename=output_filename,
            avatar_image_path=avatar_image_path,
            quote_text=quote_text,
            nickname_text=nickname_text,
            additional_image_path=additional_image_path,
            font_path=font_path,
            output_format=output_format
        )
        return res
        # return render_quote_scene(
        #     output_filename=output_filename,
        #     avatar_image_path=avatar_image_path,
        #     quote_text=quote_text,
        #     nickname_text=nickname_text,
        #     additional_image_path=additional_image_path,
        #     font_path=font_path,
        #     output_format=output_format
        # )
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

def delete_image(image_path: str) -> None:
    """
    删除指定路径的图片文件。

    :param image_path: 图片文件的绝对路径。
    """
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"Image deleted: {image_path}")
        else:
            print(f"Image not found: {image_path}")
    except Exception as e:
        print(f"Failed to delete image: {image_path}. Error: {e}")