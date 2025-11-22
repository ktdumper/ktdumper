from devices import DEVICES
import os

BUILD_DIR = "build"

HTML_PART_1 = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>List of models supported by ktdumper.</title>
    <style type="text/css">
        @media (max-width: 600px) {
            table {
                width: 100%;
                font-size: 14px;
            }

            th, td {
                padding: 1px;
            }
        }
        * {
            font-family: Arial, sans-serif;
        }
        table {
            border-collapse: collapse;
            width: 99%;
            margin: 0 auto;
        }
        
        td, th {
            border: 1px solid #ddd;
            padding: 8px;
        }
        
        tr:nth-child(even){background-color: #f2f2f2;}
        
        tr:hover {background-color: #ddd;}
        
        th {
            padding-top: 12px;
            padding-bottom: 12px;
            text-align: left;
            background-color: #00008b;
            color: white;
        }
    </style>
</head>
<body>
    <p>List of models supported by <a href="https://github.com/ktdumper/ktdumper">ktdumper</a>.</p>
    <table>
        <tr><th>Model Name</th><th>VID</th><th>PID</th><th>Supported Commands</th></tr>
"""

HTML_PART_2 = """    </table>
</body>
</html>
"""


if os.path.exists(BUILD_DIR):
    import shutil
    shutil.rmtree(BUILD_DIR)
os.makedirs(BUILD_DIR, exist_ok=True)

html_text = HTML_PART_1

for d in DEVICES:
    html_text += f"        <tr><td>{d.name.upper().replace('I', 'i')}</td><td>{d.vid:04X}</td><td>{d.pid:04X}</td><td>{', '.join(list(d.commands.keys()))}</td></tr>\n"
    
html_text += HTML_PART_2
html_path = os.path.join(BUILD_DIR, "index.html")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_text)
