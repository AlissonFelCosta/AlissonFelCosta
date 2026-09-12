#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, html, json, time, urllib.error, urllib.request
from pathlib import Path
from profile_art_config import DEFAULT_CONFIG, RevealLoop, load_config, project_path
LIGHT_PALETTE=("#ebedf0","#9be9a8","#40c463","#30a14e","#216e39"); DARK_PALETTE=("#161b22","#0e4429","#006d32","#26a641","#39d353"); MONTHS=("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")

def fetch_calendar(user, attempts):
    url=f'https://github-contributions-api.jogruber.de/v4/{user}?y=last'; req=urllib.request.Request(url,headers={'User-Agent':'profile-art-generator/1.0'}); payload=None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req,timeout=25) as r: payload=json.load(r); break
        except (TimeoutError,urllib.error.URLError,json.JSONDecodeError):
            if attempt==attempts-1: raise
            time.sleep(2**attempt)
    rows=payload.get('contributions',[]) if payload else []
    if not rows: raise RuntimeError(f'No contribution data returned for {user}')
    return sorted(rows,key=lambda x:x['date'])

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',type=Path,default=DEFAULT_CONFIG); ap.add_argument('--user'); ap.add_argument('--out',type=Path); ap.add_argument('--static',action='store_true'); o=ap.parse_args(); c=load_config(o.config,{'github_user','contributions_output','contribution_animation'}); user=o.user or c['github_user']; out=o.out or project_path(c['contributions_output']); rows=fetch_calendar(user,3)
    first=dt.date.fromisoformat(rows[0]['date']); sunday=first-dt.timedelta(days=(first.weekday()+1)%7); cells=[]; months=[]; seen=set()
    for item in rows:
        d=dt.date.fromisoformat(item['date']); off=(d-sunday).days; week=off//7; weekday=(d.weekday()+1)%7; level=max(0,min(int(item.get('level',0)),4)); count=int(item.get('count',0)); cells.append((week,weekday,d.isoformat(),count,level)); key=(d.year,d.month)
        if key not in seen: seen.add(key); months.append((week,MONTHS[d.month-1]))
    weeks=max(c[0] for c in cells)+1; step=15; left=34; top=24; width=left+weeks*step+6; height=top+7*step+30; total=sum(x[3] for x in cells); loop=RevealLoop.from_config(c['contribution_animation']); sweep=float(c['contribution_animation']['sweep_seconds']); cell=float(c['contribution_animation']['cell_seconds']); max_order=max((weeks-1)+6*.6,1)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><style>text{{font-family:ui-monospace,monospace}}.label{{fill:#7d8590;font-size:11px}}.total{{fill:#e6edf3;font-size:13px;font-weight:700}}'+''.join(f'.l{i}{{fill:{DARK_PALETTE[i]}}}' for i in range(5))+'</style>']
    for wk,label in months: parts.append(f'<text class="label" x="{left+wk*step}" y="16">{label}</text>')
    for label,row in (("Mon",1),("Wed",3),("Fri",5)): parts.append(f'<text class="label" x="2" y="{top+row*step+8}">{label}</text>')
    for week,weekday,date,count,level in cells:
        x=left+week*step; y=top+weekday*step; delay=((week+weekday*.6)/max_order)*sweep
        if o.static: parts.append(f'<rect class="l{level}" x="{x}" y="{y}" width="12" height="12" rx="2"><title>{html.escape(date)}: {count} contributions</title></rect>'); continue
        re,fs,fe=loop.opacity_key_times(delay,cell); parts.append(f'<rect class="l{level}" x="{x}" y="{y}" width="12" height="12" rx="2" opacity="0"><title>{html.escape(date)}: {count} contributions</title><animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;{re:.5f};{fs:.5f};{fe:.5f};1" begin="{delay:.3f}s" dur="{loop.duration:.2f}s" repeatCount="indefinite"/></rect>')
    parts += [f'<text class="total" x="{left}" y="{height-6}">{total:,} contributions in the last year</text>','</svg>']; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(''.join(parts),encoding='utf-8')
if __name__=='__main__': main()
