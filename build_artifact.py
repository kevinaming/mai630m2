"""Builds the single-file version for the Claude artifact: page + phrases.
Run: python3 build_artifact.py OUT.html"""
import json, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(here, "index.html")).read()
data = open(os.path.join(here, "data.js")).read()
# the artifact viewer adds its own document skeleton
html = html[html.index("<title>"):]
html = html.replace("</head>\n<body>\n", "").replace("</body>\n</html>\n", "")
html = html.replace('<script src="data.js"></script>',
                    "<script>\n" + data + "\n</script>")
open(sys.argv[1], "w").write(html)
print("written", sys.argv[1], len(html), "bytes")
