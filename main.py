import time
import os

import requests

CEPH_HOST = os.getenv("CEPH_HOST", "https://127.0.0.1:8443")
KUMA_HOST = os.getenv("KUMA_HOST", "https://127.0.0.1:3001")
CEPH_OSD_KEY = os.getenv("CEPH_OSD_KEY")
CEPH_HEALTH_KEY = os.getenv("CEPH_HEALTH_KEY")
CEPH_USERNAME = os.getenv("CEPH_USERNAME")
CEPH_PASSWORD = os.getenv("CEPH_PASSWORD")
INTERVAL = float(os.getenv("INTERVAL", 60))
VERIFY_CEPH_TLS = os.getenv("VERIFY_CEPH_TLS", "true").strip().lower() == "true"

def kuma_push(key, status="up", msg=""):
  req = f"{KUMA_HOST}/api/push/{key}?status={status}"
  if msg is not None and len(msg.strip()) > 0:
    req += f"&msg={msg}"

  print(f"Reporting to kuma that {key} is {status}")
  requests.get(req)

def ceph_osd_status(token):
  r = requests.get(f"{CEPH_HOST}/api/osd", verify=VERIFY_CEPH_TLS, headers={
    "Authorization": "Bearer " + token
  })
  r = r.json()
  down_osds = [e["osd"] for e in r if e["up"] == 0]
  if len(down_osds) > 0:
    msg = "OSDs down: " + ", ".join([str(e) for e in down_osds])
    kuma_push(CEPH_OSD_KEY, status="down", msg=msg)
    return

  kuma_push(CEPH_OSD_KEY, status="up")
  return

def ceph_health_status(token):
    r = requests.get(f"{CEPH_HOST}/api/health/minimal", verify=VERIFY_CEPH_TLS, headers={
      "Authorization": "Bearer " + token
    })
    health = r.json()["health"]
    status = health["status"]
    checks = health["checks"]
    checks_msg = "; ".join([f"""{e["summary"]["message"]} ({e["severity"]})""" for e in checks])

    if status == "HEALTH_OK" or status == "HEALTH_WARN":
      kuma_push(CEPH_HEALTH_KEY, status="up", msg=checks_msg)
      return
    else:
      kuma_push(CEPH_HEALTH_KEY, status="down", msg=checks_msg)

def get_ceph_token():
  token = requests.post(f"{CEPH_HOST}/api/auth", json={
    "username": CEPH_USERNAME,
    "password": CEPH_PASSWORD
  }, verify=False)
  return token.json()["token"]

def ceph_kuma():
  token = get_ceph_token()

  ceph_osd_status(token)
  ceph_health_status(token)

while True:
  ceph_kuma()
  time.sleep(INTERVAL)
