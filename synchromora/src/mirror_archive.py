#!/usr/bin/env python3
"""Mirror the two release ZIPs to storagecode as a redundant archive.

No asset is silently replaced or deleted. Authentication comes from a token
file or GITHUB_TOKEN and is not persisted. The competition release remains the
user-facing canonical delivery.
"""
import argparse
import hashlib
import os
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
BASE='https://api.github.com/repos/dreamer2664/storagecode'
TAG='competitionvideo28-synchromora-r02-backup'
FILES=[('00_ALL_AVAILABLE_CLIPS_AND_SRT_r02.zip','7c0c6a35a5e6b3855a170e11dd4ee5a862797c7174c5971d0c71140e83be2d42'),
       ('99_REBUILD_KIT_PARTIAL_r02.zip','b6339d2f18e4c65260ab758ca72ffda443bdf4c4614370ec1966f6566b136b72')]
BODY='''Redundant storagecode archive for the synchromora 15/18 partial Shorts delivery.\n\nCanonical user-facing release, individual MP4s, credits, caveats and QC: https://github.com/dreamer2664/competitionvideo28/releases/tag/synchromora-clips-20261028-r02\n\nThe ZIPs contain the 15 available clips and editable reconstruction materials. The age-restricted first source and its three requested clips are not included. Captions are machine-generated and rights are not verified.\n\nSHA-256: `00_ALL_AVAILABLE_CLIPS_AND_SRT_r02.zip` = `7c0c6a35a5e6b3855a170e11dd4ee5a862797c7174c5971d0c71140e83be2d42`; `99_REBUILD_KIT_PARTIAL_r02.zip` = `b6339d2f18e4c65260ab758ca72ffda443bdf4c4614370ec1966f6566b136b72`.\n'''

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument('--token-file',type=Path);p.add_argument('--dir',type=Path,default=ROOT/'work');a=p.parse_args()
 token=os.environ.get('GITHUB_TOKEN') or (a.token_file.read_text().strip() if a.token_file else '')
 if not token:raise SystemExit('Missing GITHUB_TOKEN or --token-file')
 s=requests.Session();s.headers.update({'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json',
   'X-GitHub-Api-Version':'2022-11-28','User-Agent':'synchromora-archive'})
 x=None;page=1
 while True:
  r=s.get(BASE+'/releases',params={'per_page':100,'page':page},timeout=60);r.raise_for_status()
  releases=r.json();x=next((v for v in releases if v['tag_name']==TAG),None)
  if x or len(releases)<100:break
  page+=1
 if not x:
  r=s.post(BASE+'/releases',json={'tag_name':TAG,'target_commitish':'main','name':'Backup — synchromora Shorts partial 15/18',
    'body':BODY,'draft':True,'prerelease':True},timeout=60);r.raise_for_status();x=r.json()
 print('ARCHIVE RELEASE',x['id'],'draft',x['draft'],flush=True)
 for name,expected in FILES:
  path=a.dir/name
  if digest(path)!=expected:raise RuntimeError('Local archive hash mismatch: '+name)
  asset=next((z for z in x['assets'] if z['name']==name),None)
  if not asset:
   print('ARCHIVE UPLOAD',name,path.stat().st_size,flush=True)
   with path.open('rb') as f:
    r=s.post(x['upload_url'].split('{')[0],params={'name':name},headers={'Content-Type':'application/zip'},data=f,timeout=(30,1200))
   r.raise_for_status();asset=r.json()
  if asset.get('size')!=path.stat().st_size or asset.get('digest')!='sha256:'+expected:
   raise RuntimeError('Archive asset differs; refusing to overwrite '+name)
  r=s.get(asset['url'],headers={'Accept':'application/octet-stream'},stream=True,timeout=(30,600));r.raise_for_status()
  if 'json' in r.headers.get('Content-Type',''):raise RuntimeError('Asset request returned metadata, not media')
  h=hashlib.sha256();n=0
  for chunk in r.iter_content(1024*1024):
   if chunk:h.update(chunk);n+=len(chunk)
  if h.hexdigest()!=expected or n!=path.stat().st_size:raise RuntimeError('Archive download mismatch: '+name)
  print('ARCHIVE VERIFIED',name,n,expected,flush=True)
  x=requests_retry_get(s, x['url'])
 if x['draft']:
  r=s.patch(x['url'],json={'draft':False,'prerelease':True,'body':BODY},timeout=60);r.raise_for_status();x=r.json()
 if x['draft'] or not x['prerelease']:raise RuntimeError('Archive publication state not as expected')
 print('ARCHIVE PUBLISHED',x['html_url'],flush=True)

def requests_retry_get(s,url):
 r=s.get(url,timeout=60);r.raise_for_status();return r.json()

if __name__=='__main__':main()
