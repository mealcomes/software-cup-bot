from graphviz import Source
import io


def render_mindmap(dot_code):
    """
    接收 Dot 代码字符串，直接在内存中渲染为 PNG 图像并返回图像的字节流。

    :param dot_code: Dot 语言格式的字符串
    :return: 包含 PNG 图像数据的字节流
    """
    # 创建 Source 对象
    source=Source(dot_code)

    # 使用 pipe 方法直接在内存中渲染图像为 PNG 格式
    png_bytes=source.pipe(format='png')

    return png_bytes
