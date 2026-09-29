"""Build the page from src/page.src.html plus the models.

Run from the repo root:  python src/build.py
Writes index.html (full document, for GitHub Pages) and src/artifact.html (fragment, for the claude.ai copy).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda *p: open(os.path.join(ROOT, *p), encoding='utf-8').read()
REPO = 'https://github.com/opitaru-sys/forever-warlock-lab'
RESULTS = REPO + '/issues/new?template=test-result.yml'

import base64, json
icon_dir = os.path.join(ROOT, 'assets', 'icons')
ICONS = {f[:-4]: 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(icon_dir, f), 'rb').read()).decode()
         for f in sorted(os.listdir(icon_dir)) if f.endswith('.jpg')}
src = rd('src', 'page.src.html')
body = (src.replace('/*MODEL*/', rd('model.js')).replace('/*LEVELING*/', rd('leveling.js')).replace('/*BUILDER*/', rd('src', 'builder.js')).replace('/*ICONS*/', json.dumps(ICONS))
        .replace("const REPO_URL = '';", "const REPO_URL = %r;" % REPO).replace("const RESULTS_URL = '';", "const RESULTS_URL = %r;" % RESULTS))
open(os.path.join(ROOT, 'src', 'artifact.html'), 'w', encoding='utf-8').write(body)
head_extra = ('<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
              '<meta name="darkreader-lock">\n<style>[hidden]{display:none!important}</style>\n')
end = body.index('</style>') + len('</style>')
doc = '<!doctype html>\n<html lang="en">\n<head>\n' + head_extra + body[:end] + '\n</head>\n<body>\n' + body[end:] + '\n</body>\n</html>\n'
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(doc)
print('index.html', len(doc), 'chars; src/artifact.html', len(body), 'chars')
