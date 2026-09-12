#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, json
from pathlib import Path
from profile_art_config import DEFAULT_CONFIG, load_config, project_path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',type=Path,default=DEFAULT_CONFIG); ap.add_argument('--out',type=Path); o=ap.parse_args(); c=load_config(o.config,{'tech_stack_output','tech_stack'}); out=o.out or project_path(c['tech_stack_output'])
    items=c['tech_stack']; cols=4; w=820; h=270; parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><style>.t{{fill:#d8dee9;font:600 18px ui-monospace,monospace}}.s{{fill:#7d8590;font:13px ui-monospace,monospace}}</style><rect x="1" y="1" width="818" height="268" rx="12" fill="#0d1117" stroke="#30363d"/>']
    for i,(name,kind) in enumerate(items):
        col=i%cols; row=i//cols; x=45+col*200; y=50+row*72; parts.append(f'<rect x="{x}" y="{y}" width="42" height="42" rx="10" fill="#18243a" stroke="#31558e"/><text x="{x+21}" y="{y+27}" text-anchor="middle" style="fill:#58a6ff;font:700 13px Arial">{html.escape(name[:3].upper())}</text><text class="t" x="{x+54}" y="{y+20}">{html.escape(name)}</text><text class="s" x="{x+54}" y="{y+38}">{html.escape(kind)}</text>')
    parts.append('</svg>'); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(''.join(parts),encoding='utf-8')
if __name__=='__main__': main()
