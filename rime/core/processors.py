from rime.core import RimeCore
import markdown

@RimeCore.register_processor('.md')
def process_markdown(source):
    return markdown.markdown(source)
