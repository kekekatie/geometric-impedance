from pathlib import Path
import base64,html,shutil,zipfile
root=Path(__file__).resolve().parent; src=root/'local-response'
text=(src/'READ-ME-FIRST.md').read_text(encoding='utf-8')
page='<meta charset="utf-8"><title>One neighbour settles an option</title><style>body{font:18px system-ui;line-height:1.5;max-width:1250px;margin:24px auto;padding:0 16px}img{width:100%}pre{white-space:pre-wrap;font:inherit}</style><h1>One neighbour settles an open option</h1><p>Of 19 additions, one particular tile is enough to remove the second option. Leave it out, and both remain.</p><img alt="Before, decisive tile alone, full construction step" src="data:image/png;base64,'+base64.b64encode((src/'local-response.png').read_bytes()).decode()+'"><pre>'+html.escape(text)+'</pre>'
(src/'OPEN-LOCAL-RESPONSE.html').write_text(page,encoding='utf-8')
