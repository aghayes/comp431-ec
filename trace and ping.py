import sys
import subprocess
import re
import pandas as pd
import threading
import datetime
def tap(url):
    route = subprocess.run(f"traceroute {url}", shell=True, capture_output=True, encoding='utf-8')
    with open(f"{sys.argv[1]}_{datetime.datetime.now()}.txt".replace(":", "-"), "x") as f:
        f.write(route.stdout)
    ips = re.findall("\\((\\d*\\.\\d*\\.\\d*\\.\\d*)\\)", route.stdout)[1:]
    print(ips)
    return ips


def pt(ip, arr):
    p = subprocess.run(f"ping {ip} -c 60", shell=True, capture_output=True, encoding='utf-8')
    received = re.findall("(\\d*) received", p.stdout)[0]
    if received != "0":
        stats = re.findall("= (.*) ms", p.stdout)[0].split("/")
        stats.insert(0, received)
        stats.insert(0, ip)
    else:
        stats = [ip, received, 0,0,0,0]
    row = pd.DataFrame([stats], columns=["ip", "received", "min", "avg", "max", "mdev"])
    arr.append(row)


ips = tap(sys.argv[1])
df = pd.DataFrame()
rows = []
threads = [threading.Thread(target=pt, args=(ip, rows)) for ip in ips]
for thread in threads: 
    thread.start()
for thread in threads:
    thread.join()
for row in rows:
    df=df.append(row)
ip_frame = pd.DataFrame([ips])
ip_frame = ip_frame.transpose()
print(ip_frame)
df = ip_frame.merge(df, how="left", left_on=0, right_on="ip")
df = df.drop(columns=[0])
print(df)
df.to_csv(f"{sys.argv[1]}_{datetime.datetime.now()}.csv", index=False)
