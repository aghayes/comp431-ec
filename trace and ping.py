import sys
import subprocess
import re
import pandas as pd


def tap(url):
    route = subprocess.run(f"tracert {url}", shell=True, capture_output=True, encoding='utf-8')
    ips = re.findall("\\[(\\d*\\.\\d*\\.\\d*\\.\\d*)\\]", route.stdout)[1:]
    return ips


def pt(ip, df):
    p = subprocess.call(f"ping {ip} -c 60")
    received = re.findall("(\\d*) received")
    stats = re.findall("= (.*) ms").split("/")
    stats.insert(0, received[0])
    stats.insert(0, ip)
    row = pd.DataFrame([stats], columns=["ip", "received", "min", "avg", "max", "mdev"])
    df.append(row)


ips = tap(sys.argv[1])
df = pd.DataFrame()
for ip in ips:
    pt(ip, df)
print(df)