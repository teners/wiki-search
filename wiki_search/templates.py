from pathlib import Path

from jinja2 import Template

__all__ = ('search_result_template',)


with open(Path('wiki_search/static/search_result.html')) as template:
    search_result_template = Template(template.read())
