#!/usr/bin/env python3
from __future__ import annotations
import argparse, html
from pathlib import Path
from profile_art_config import DEFAULT_CONFIG, load_config, project_path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',type=Path,default=DEFAULT_CONFIG); ap.add_argument('--out',type=Path); ap.add_argument('--static',action='store_true'); o=ap.parse_args()
    c=load_config(o.config,{'wordmark','wordmark_output'}); out=o.out or project_path(c['wordmark_output']); text=c['wordmark'];
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 210" width="760" height="210" role="img" aria-label="{html.escape(text)}"><defs><linearGradient id="g"><stop stop-color="#1683ff"/><stop offset="1" stop-color="#7a4dff"/></linearGradient></defs><rect width="100%" height="100%" fill="none"/><text x="380" y="95" text-anchor="middle" font-family="Futura,Montserrat,Arial,sans-serif" font-size="72" font-weight="800" letter-spacing="8" fill="url(#g)">{html.escape(text)}</text><text x="380" y="150" text-anchor="middle" font-family="ui-monospace,monospace" font-size="18" fill="#aab6d3">&lt; código • ideias • resultados &gt;</text></svg>'''
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(svg,encoding='utf-8')
if __name__=='__main__': main()
