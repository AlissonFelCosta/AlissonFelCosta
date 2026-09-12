#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, os, urllib.request
from pathlib import Path
from profile_art_config import DEFAULT_CONFIG, load_config, project_path

def headers():
    h={'Accept':'application/vnd.github+json','User-Agent':'profile-art-generator/1.0'}
    token=os.getenv('GITHUB_TOKEN')
    if token: h['Authorization']=f'Bearer {token}'
    return h

def fetch_languages(user: str):
    page=1; totals={}
    while page<=10:
        url=f'https://api.github.com/users/{user}/repos?per_page=100&page={page}&type=owner&sort=updated'
        with urllib.request.urlopen(urllib.request.Request(url,headers=headers()),timeout=30) as r:
            repos=json.load(r)
        if not repos: break
        for repo in repos:
            if repo.get('fork'): continue
            with urllib.request.urlopen(urllib.request.Request(repo['languages_url'],headers=headers()),timeout=20) as r:
                data=json.load(r)
            for k,v in data.items(): totals[k]=totals.get(k,0)+int(v)
        if len(repos)<100: break
        page+=1
    return totals

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',type=Path,default=DEFAULT_CONFIG); ap.add_argument('--user'); ap.add_argument('--out',type=Path); o=ap.parse_args()
    c=load_config(o.config,{'github_user','language_stats_output','language_stats'}); user=o.user or c['github_user']; out=o.out or project_path(c['language_stats_output'])
    totals=fetch_languages(user); excluded=set(c['language_stats'].get('excluded',[])); ranked=sorted(((k,v) for k,v in totals.items() if k not in excluded),key=lambda x:x[1],reverse=True)[:int(c['language_stats'].get('top',6))]; s=sum(v for _,v in ranked) or 1
    W,H=760,390; cx,cy,r=170,195,105
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><style>.l{{fill:#c9d1d9;font:15px ui-monospace,monospace}}.p{{fill:#7d8590;font:12px ui-monospace,monospace}}</style><rect width="100%" height="100%" rx="12" fill="#0d1117" stroke="#30363d"/>']
    colors=['#58a6ff','#f2cc60','#f0883e','#bc8cff','#ff7b72','#39d353']; start=-math.pi/2
    for i,(name,val) in enumerate(ranked):
        frac=val/s; end=start+frac*2*math.pi; large=1 if end-start>math.pi else 0; x1=cx+r*math.cos(start); y1=cy+r*math.sin(start); x2=cx+r*math.cos(end); y2=cy+r*math.sin(end)
        parts.append(f'<path d="M {cx} {cy} L {x1:.2f} {y1:.2f} A {r} {r} 0 {large} 1 {x2:.2f} {y2:.2f} Z" fill="{colors[i%len(colors)]}"/>'); start=end
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="62" fill="#0d1117"/><text x="{cx}" y="{cy-4}" text-anchor="middle" class="l">Top {len(ranked)}</text><text x="{cx}" y="{cy+18}" text-anchor="middle" class="p">linguagens</text>')
    for i,(name,val) in enumerate(ranked):
        pct=val/s*100; y=85+i*42; parts.append(f'<circle cx="380" cy="{y-5}" r="6" fill="{colors[i%len(colors)]}"/><text x="398" y="{y}" class="l">{name}</text><text x="705" y="{y}" text-anchor="end" class="l">{pct:.1f}%</text>')
    parts.append('</svg>'); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(''.join(parts),encoding='utf-8')

if __name__=='__main__': main()
