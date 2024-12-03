from manim import *
import os
import numpy as np
# from PIL import Image
from datetime import datetime  # 导入 datetime 模块


class QuoteScene(Scene):
    def __init__(
            self,
            avatar_image_path: str,
            quote_text: str,
            nickname_text: str,
            additional_image_path: str,
            font_path: str,
            *args, **kwargs
        ):
        self.avatar_image_path = avatar_image_path
        self.quote_text = quote_text
        self.nickname_text = nickname_text
        self.additional_image_path = additional_image_path
        self.font_path = font_path
        super().__init__(*args, **kwargs)

    def construct(self):
        MyTexTemplate = TexTemplate(
            tex_compiler="xelatex",
            output_format='.xdv',
        )
        MyTexTemplate.add_to_preamble(r"\usepackage{fontspec}\setmainfont{Source Han Serif SC}")

        avatar_image_mobject = ImageMobject(self.avatar_image_path)
        avatar_image_mobject.set_height(config.frame_height)  # 设置高度
        avatar_image_mobject.to_edge(LEFT, buff=0).set_z_index(1)  # 贴靠左侧
        self.add(avatar_image_mobject)
        # self.play(FadeIn(avatar_image_mobject))

        # 使用 PNG 图片作为纹理
        script_path = os.path.abspath(__file__)
        mask_path = os.path.join(os.path.dirname(script_path),
                            'static', 'resource', 'images', 'mask.png' )
        # mask_img = ImageMobject("static/resource/images/mask.png")  # 自行准备 PNG 图像
        mask_img = ImageMobject(mask_path)  # 自行准备 PNG 图像
        mask_img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])  # 平滑处理
        mask_img.scale(2).set_z_index(2)  # 调整大小

        # 添加到场景中
        self.add(mask_img)
        # self.play(FadeIn(mask_img))

        # self.play( Create( SurroundingRectangle(mask_img) ) )
        # self.wait(2)

        # quote_text = Text(self.quote_text,
        #                   font=self.font_path,
        #                   font_size=72)
        # quote_text.set_z_index(3).shift(RIGHT * 2)
        # # self.add(text)
        # self.play(Write(quote_text))
        # self.wait(2)

        segments = split_text_by_punctuation(self.quote_text)
        print("qwq segments = ", segments)

        # 创建每一行的 Text 对象
        y_offset = 0
        text_objects = []
        text_objects.append(Text(""))

        for segment in segments:
            print("self.font_path = ", self.font_path)
            # with register_font(self.font_path):
            # a = Text("Hello", font="Custom Font Name")
            # text_obj = Text(segment,
            #                 # font=self.font_path,
            #                 font="sans-serif",
            #                 font_size=36)
            text_obj = Tex(
                segment,
                tex_template=MyTexTemplate,
                font_size=32
            )
            text_obj.move_to(ORIGIN).shift(RIGHT * 2.5 + UP * 3).set_z_index(3)

            self.add(text_obj)
            text_obj.shift(UP * y_offset)

            if not text_objects:
                pass
            else:
                text_obj.align_to(text_objects[0], LEFT)

            text_objects.append(text_obj)
            y_offset -= 0.6  # 设定行与行之间的间隔

        # print("qwq text_obj = ", text_objects)

        # 将所有 Text 对象添加到场景中
        # self.play(*[Write(text_obj) for text_obj in text_objects])
        # write_animations = [Write(t, run_time=1) for t in text_objects]
        # print("qwq, write_animations = ", write_animations)
        # print( "qwq, *w_a = ", *write_animations )
        # write_animation_group = AnimationGroup(*write_animations, lag_ratio=0.5)
        # print("qwq get all mobjects = ", write_animation_group.get_all_mobjects())
        # print("qwq, write_animation_group = ", write_animation_group)
        # self.play(write_animation_group)

        # for t in text_objects:
        #     print("qwq this t is: ", t)
        #     self.play(
        #         Write(t)
        #     )
        #
        # self.wait(1)

        # 如果没有就传空串
        if self.additional_image_path != "":
            additional_image = ImageMobject(self.additional_image_path)

            # additional_image.scale(quote_text_width / image_width * 0.8)
            additional_image.set_width(3)
            # additional_image.next_to(text_objects[0], UP).set_z_index(3)
            additional_image.to_edge(UP).to_edge(RIGHT)
            additional_image.shift(LEFT*0.8+DOWN*0.6)
            additional_image.set_z_index(3)
            
            quote_text_group = VGroup(*text_objects)
            quote_text_group.next_to(additional_image, DOWN)
            quote_text_group.align_to(additional_image, LEFT)

            # image_width = additional_image.width
            # image_height = additional_image.height
            
            # quote_group = Group(additional_image, *text_objects)
            # print("qwq quote_image_and_text_group = ", quote_group)
            # quote_group.shift(DOWN * 5 / image_width * image_height )

            self.add(additional_image)

        nickname_text = Text("——{}".format(self.nickname_text), font=self.font_path)
        nickname_text.to_edge(DOWN).shift(RIGHT * 2.5).set_z_index(3)
        self.add(nickname_text)


def split_text_by_punctuation(text):
    """
    按照逗号、句号等标点符号分割文本，并在符号后添加换行
    """
    # 定义中文和英文的标点符号
    punctuation = ["，", "。", ",", "."]
    segments = []
    current_segment = ""
    current_len = 0

    for char in text:
        current_segment += char
        current_len += 1
        if (char in punctuation) or (current_len >= 10):
            segments.append(current_segment.strip())
            current_segment = ""
            current_len = 0

    # 如果有剩余的文本，加入最后一个段落
    if current_segment:
        segments.append(current_segment.strip())

    return segments


# 定义渲染函数
def render_quote_scene_Tex(
        output_filename: str,
        avatar_image_path: str,
        quote_text: str,
        nickname_text: str,
        additional_image_path: str,
        font_path: str = "",
        output_format: str = "png"
) -> str:
    """
    渲染 ImageWithGradientMask 场景，并保存为 GIF 文件。

    参数：
        avatar_image_path (str): 要加载的图片路径。
        quote_text (str): 显示的文本内容。
    """
    # config.media_width = "1920px"  # 设置视频宽度
    # config.media_width = "300px"  # 设置较低的分辨率
    config.frame_rate = 15  # 降低帧率
    # config.pixel_height = 300
    # config.pixel_width = 400
    # config.frame_height = 300
    # config.frame_width = 400
    config["format"] = output_format  # 指定输出格式为 GIF
    # config.output_file = "./output.png"
    config.output_file = output_filename
    # must be in [None, 'png', 'gif', 'mp4', 'mov', 'webm']
    # config["write_to_movie"] = True  # 启用写入文件

    scene = QuoteScene(avatar_image_path,
                       quote_text,
                       nickname_text,
                       additional_image_path,
                       font_path)
    scene.render()

    script_path = os.path.abspath(__file__)
    print("abspath = ", script_path)

    result_image_path = os.path.join(
        os.path.dirname(script_path),
        'media', 'images', config.output_file
    )
    print("result_image_path =", result_image_path)
    return result_image_path


"""
python QuoteScene.py
"""
if __name__ == "__main__":
    # 示例调用 test
    render_quote_scene(
        output_filename="output.png",
        avatar_image_path="static/resource/images/呆萌.jpg",
        quote_text="你好你好你好你好，你好你好你好你好你好你好你好",
        nickname_text="qwq",
        additional_image_path="static/resource/images/熊大.jpg",
        # font_path=r"D:\AAAstuffsAAA\AAAqwqAAA\AAArepo-from-github-giteeAAA\github\nonebot_plugin_Q_fork\PingFang_SC_Semibold.ttf"
        # font_path='Microsoft JhengHei UI'
        font_path='Source Han Serif SC'
    )
