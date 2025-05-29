from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from urllib.parse import urlparse
from pathlib import Path
import shutil

from src.data import Data


this_dir = Path(__file__).parent
data = Data.load(this_dir / "data")
template_dir = this_dir / "templates"
output_dir = this_dir / "output"

loader = FileSystemLoader(template_dir)
env = Environment(loader=loader, autoescape=select_autoescape())

def get_domain(url: str) -> str:
    result = urlparse(url).netloc
    if result.startswith("www."):
        result = result[4:]
    return result

if output_dir.exists():
    print(f"Deleting '{output_dir}'...")
    shutil.rmtree(output_dir)

for file in ["index.html", "about.html"]:
    print(f"Rendering '{file}'...")
    template = env.get_template(file)
    output_path = output_dir / file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as fh:
        content = template.render(data=data, get_domain=get_domain)
        fh.write(content)
