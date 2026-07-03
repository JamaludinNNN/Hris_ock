import subprocess
import time
import os

process = subprocess.Popen(['npx', 'localtunnel', '--port', '8000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

for i in range(15):
    line = process.stdout.readline()
    if 'your url is' in line:
        print(line.strip())
        break
    time.sleep(1)
