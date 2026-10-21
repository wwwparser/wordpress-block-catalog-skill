"""Build the standalone public learning site from authored lesson fragments."""
import html
import json
import shutil
import zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
site = ROOT / 'tutorial'
from tutorial_lessons import chapters
toc = ''.join(f'<a href="#{c["id"]}"><b>{i:02}</b><span>{html.escape(c["title"])}</span></a>' for i, c in enumerate(chapters, 1))
sections = ''.join(f'<section class="chapter" id="{c["id"]}"><div class="chapter-head"><span class="chapter-number">{i:02}</span><h2>{html.escape(c["title"])}</h2></div><p class="goal">{html.escape(c["goal"])}</p>{c["body"]}<label class="complete"><input type="checkbox" data-chapter="{c["id"]}">Я изучил этот этап</label></section>' for i, c in enumerate(chapters, 1))
template = (ROOT / 'templates/tutorial.html').read_text(encoding='utf-8')
(site / 'index.html').write_text(template.replace('{{TOC}}', toc).replace('{{SECTIONS}}', sections).replace('{{COUNT}}', str(len(chapters))), encoding='utf-8')
assets = site / 'assets'
assets.mkdir(exist_ok=True)
for name, source in [('desktop.png','prototype-1440.png'),('mobile.png','prototype-390.png'),('product.png','prototype-product.png'),('editor.png','prototype-editor.png')]:
    original = ROOT / 'research' / source
    if original.exists():
        shutil.copyfile(original, assets / name)
    elif not (assets / name).exists():
        raise FileNotFoundError(f'Missing screenshot: {source}; initialize tutorial submodule or capture the demo')
downloads = site / 'downloads'
downloads.mkdir(exist_ok=True)
source_root = site / 'source'
source_root.mkdir(exist_ok=True)
files = [
    ROOT / 'wordpress/wp-content/plugins/cerlab-catalog/cerlab-catalog.php',
    ROOT / 'wordpress/wp-content/plugins/cerlab-catalog/admin.js',
    ROOT / 'wordpress/wp-content/plugins/cerlab-catalog/editor.js',
    ROOT / 'scripts/install-local.php', ROOT / 'scripts/setup_local.py',
    ROOT / 'scripts/router.php', ROOT / 'scripts/check_demo.py',
    ROOT / 'scripts/download_runtime.py', ROOT / 'scripts/collect_reference.py',
    ROOT / 'scripts/prepare_media.py', ROOT / 'scripts/package_wordpress.py',
    ROOT / 'src/services/reference_client.py', ROOT / 'start.ps1',
    ROOT / 'research/verification.json', ROOT / 'research/catalogue.json',
    ROOT / 'README.md', ROOT / 'docs/EDITING.md',
]
files += [p for p in (ROOT / 'wordpress/wp-content/themes/cerlab-child').rglob('*') if p.is_file() and '/media/' not in p.as_posix()]
files += [p for p in (ROOT / 'skill/wordpress-block-catalog').rglob('*') if p.is_file()]
with zipfile.ZipFile(downloads / 'authored-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in files:
        relative = path.relative_to(ROOT)
        archive.write(path, relative.as_posix())
        dest = source_root / (relative.as_posix() + '.txt')
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
(site / '.nojekyll').touch()
print(f'Built {len(chapters)} lessons; published files contain no runtime or credentials')
