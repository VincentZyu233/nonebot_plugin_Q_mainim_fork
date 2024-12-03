from manim import *
import os


def foo():
    script_path = os.path.abspath(__file__)
    print("abspath = ", script_path)

    new_path = os.path.join(os.path.dirname(script_path),
                            'media', 'images', 'qwq.png')
    print("New path =", new_path)

    

def list_fonts():
    import matplotlib.font_manager as font_manager
    # 获取系统中的所有字体
    fonts = font_manager.findSystemFonts()
    
    # 用于存储字体名称的集合
    font_names = set()
    
    # 遍历所有字体文件并提取字体名称
    for font in fonts:
        try:
            # 使用 font_manager 的 FontProperties 来获取字体名称
            font_properties = font_manager.FontProperties(fname=font)
            font_name = font_properties.get_name()
            font_names.add(font_name)
        except Exception as e:
            print(f"Error processing {font}: {e}")
    
    # 打印所有字体名称
    for font_name in sorted(font_names):
        print(font_name)


def list_pango_fonts():
    import manimpango
    print("manimpango font list: ", manimpango.list_fonts())

if __name__ == "__main__":
    list_fonts()
    # foo()
    list_pango_fonts()


class FontTestScene(Scene):
    """
    manim -pql SomeTests.py FontTestScene
    """

    def construct(self):
        import requests
        import zipfile
        import re
        import io
        from pathlib import Path
        a = requests.get(
            # "https://github.com/atelier-anchor/smiley-sans/releases/download/v1.1.1/smiley-sans-v1.1.1.zip"
            "https://github.com/adobe-fonts/source-han-serif/releases/download/2.003R/09_SourceHanSerifSC.zip"
        )
        z = zipfile.ZipFile(io.BytesIO(a.content))
        font_names = [name for name in z.namelist() if re.search('\.ttf$|\.otf$', name)]
        print(font_names)

        z.extractall(path="static/resource/fonts", members=font_names)
        for i, font_name in enumerate(font_names):
            MyTexTemplate = TexTemplate(
                tex_compiler="xelatex",
                output_format='.xdv',
            )
            MyTexTemplate.add_to_preamble(rf"\usepackage{{fontspec}}\setmainfont{{{font_names[1]}}}[Path=./fonts/]")
            tex = Tex(
                # r"得意黑",
                r"得意黑",
                tex_template=MyTexTemplate,
                color=BLUE,
            ).scale(2).move_to([0, 3 - i, 0], aligned_edge=LEFT)
            self.add(tex)
            fname = Text(font_name).move_to([0, 3 - i, 0], aligned_edge=RIGHT)
            self.add(fname)


class LocalFontTestScene(Scene):
    """
        manim -pql SomeTests.py LocalFontTestScene
    """
    def construct(self):
        # 本地字体文件夹路径
        font_folder = "./static/resource/fonts/OTF/SimplifiedChinese/"

        # 获取字体文件列表
        font_names = [f for f in os.listdir(font_folder) if f.endswith(('.ttf', '.otf'))]
        print(f"Found fonts: {font_names}")

        # 遍历字体文件并渲染
        for i, font_name in enumerate(font_names):
            # 创建 TexTemplate 并设置字体
            MyTexTemplate = TexTemplate(
                tex_compiler="xelatex",
                output_format='.xdv',
            )
            MyTexTemplate.add_to_preamble(rf"\usepackage{{fontspec}}\setmainfont{{{font_name}}}[Path=./local_fonts/]")

            # 创建 Tex 对象并设置文本内容
            tex = Tex(
                r"得意黑",
                tex_template=MyTexTemplate,
                color=BLUE,
            ).scale(2).move_to([0, 3 - i, 0], aligned_edge=LEFT)
            self.add(tex)

            # 显示字体文件名
            fname = Text(font_name).move_to([0, 3 - i, 0], aligned_edge=RIGHT)
            self.add(fname)

class LocalFontTestScene2(Scene):
    """
        manim -pql SomeTests.py LocalFontTestScene2
        manim -pqh SomeTests.py LocalFontTestScene2
    """
    def construct(self):

        MyTexTemplate = TexTemplate(
            tex_compiler="xelatex",
            output_format='.xdv',
        )
        MyTexTemplate.add_to_preamble(r"\usepackage{fontspec}\setmainfont{Source Han Serif SC}")

        tex = Tex(
            "你好你好你好你好你好",
            tex_template=MyTexTemplate,
            color = BLUE,
        ).scale(2.5)
        self.add(tex)


class TestClass(Scene):
    def construct(self):
        # 使用 PNG 图片作为纹理
        img = ImageMobject("static/resource/images/mask.png")  # 自行准备 PNG 图像
        img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])  # 平滑处理
        img.scale(2)  # 调整大小

        # 添加到场景中
        self.add(img)
        self.wait(2)


"""
manim -ql QuoteScene.py GradientOpacityWithImage
"""
