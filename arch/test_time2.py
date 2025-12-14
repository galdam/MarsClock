
import time

print(f"""
{time.gmtime()}
{time.mktime(time.gmtime())}
{time.localtime()}
{time.mktime(time.localtime())}
""")