#!/usr/bin/env python3
"""Mirror the two ZIPs of a published competition release to storagecode.

Before upload, local ZIPs must match GitHub's canonical release digests. No
asset is silently replaced or deleted. Authentication comes from a token file
or GITHUB_TOKEN and is not persisted. The competition release stays canonical.
"""
import argparse
import hashlib
import os
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
BASE='https://api.github.com/repos/dreamer2664/storagecode'
CANONICAL='https://api.github.com/repos/dreamer2664/competitionvideo28'

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def json_get(s,url,**kwargs):
 r=s.get(url,timeout=60,**kwargs);r.raise_for_status();return r.json()

def main():
 p=argparse.ArgumentParser();p.add_argument('--token-file',type=Path);p.add_argument('--dir',type=Path,default=ROOT/'work')
 p.add_argument('--canonical-tag',required=True);p.add_argument('--archive-tag',required=True)
 p.add_argument('--delivery-name',required=True);p.add_argument('--recovery-name',required=True);a=p.parse_args()
 token=os.environ.get('GITHUB_TOKEN') or (a.token_file.read_text().strip() if a.token_file else '')
 if not token:raise SystemExit('Missing GITHUB_TOKEN or --token-file')
 s=requests.Session();s.headers.update({'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json',
   'X-GitHub-Api-Version':'2022-11-28','User-Agent':'synchromora-archive'})
 canonical=json_get(s,CANONICAL+'/releases/tags/'+a.canonical_tag)
 files=[]
 for name in [a.delivery_name,a.recovery_name]:
  path=a.dir/name;expected=digest(path);remote=next((x for x in canonical['assets'] if x['name']==name),None)
  if not remote or remote['size']!=path.stat().st_size or remote.get('digest')!='sha256:'+expected:
   raise RuntimeError('Local file does not match canonical release: '+name)
  files.append((name,expected))
 body=('Redundant storagecode archive for the synchromora 15/18 partial Shorts delivery.\n\n'
       'Canonical user-facing release, individual MP4s, credits, caveats and QC: '+canonical['html_url']+'\n\n'
       'The ZIPs contain the 15 available clips and editable reconstruction materials. The age-restricted first source and its three requested clips are not included. Captions are machine-generated and rights are not verified.\n\n'
       +''.join(f'- `{name}` SHA-256 `{h}`\n' for name,h in files))
 x=None;page=1
 while True:
  releases=json_get(s,BASE+'/releases',params={'per_page':100,'page':page})
  x=next((v for v in releases if v['tag_name']==a.archive_tag),None)
  if x or len(releases)<100:break
  page+=1
 if not x:
  r=s.post(BASE+'/releases',json={'tag_name':a.archive_tag,'target_commitish':'main','name':'Backup — synchromora Shorts partial 15/18',
    'body':body,'draft':True,'prerelease':True},timeout=60);r.raise_for_status();x=r.json()
 print('ARCHIVE RELEASE',x['id'],'draft',x['draft'],flush=True)
 for name,expected in files:
  path=a.dir/name;asset=next((z for z in x['assets'] if z['name']==name),None)
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
  x=json_get(s,x['url'])
 if x['draft']:
  r=s.patch(x['url'],json={'draft':False,'prerelease':True,'body':body},timeout=60);r.raise_for_status();x=r.json()
 if x['draft'] or not x['prerelease']:raise RuntimeError('Archive publication state not as expected')
 print('ARCHIVE PUBLISHED',x['html_url'],flush=True)

if __name__=='__main__':main()
