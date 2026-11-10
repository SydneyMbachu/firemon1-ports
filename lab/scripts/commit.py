#!/usr/bin/env python3
"""Explicitly commit PAN-OS candidate config and wait for the commit job."""
import os
import ssl
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

host = os.environ['PANOS_HOSTNAME']
key = os.environ['PANOS_API_KEY']
context = ssl.create_default_context(cafile=os.environ.get('PANOS_CA_FILE'))

def request(values):
    req = urllib.request.Request(
        f'https://{host}/api/',
        data=urllib.parse.urlencode(values).encode(),
        headers={'X-PAN-KEY': key},
    )
    with urllib.request.urlopen(req, context=context, timeout=30) as response:
        root = ET.fromstring(response.read())
    if root.get('status') != 'success':
        raise RuntimeError(ET.tostring(root, encoding='unicode'))
    return root

root = request({'type': 'commit', 'cmd': '<commit></commit>'})
job = root.findtext('.//job')
if not job:
    raise SystemExit('No commit job returned; inspect candidate configuration and commit response.')
for _ in range(120):
    result = request({'type': 'op', 'cmd': f'<show><jobs><id>{int(job)}</id></jobs></show>'})
    if result.findtext('.//status') == 'FIN':
        if result.findtext('.//result/job/result') != 'OK':
            raise SystemExit(ET.tostring(result, encoding='unicode'))
        print(f'Commit job {job}: OK')
        break
    time.sleep(5)
else:
    raise SystemExit(f'Commit job {job} did not finish within ten minutes; inspect on firewall.')
