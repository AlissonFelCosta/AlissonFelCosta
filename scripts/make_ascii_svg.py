#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, xml.etree.ElementTree as ET
from pathlib import Path
from profile_art_config import DEFAULT_CONFIG, RevealLoop, load_config, project_path

CANVAS_W, CANVAS_H, PAD, TITLEBAR_H = 840, 875, 20, 30
BG, BG2, FRAME, TITLE_TEXT, INK = "#0d1117", "#111722", "#30363d", "#7d8590", "#c9d1d9"

def read_rows(source: Path):
    root = ET.parse(source).getroot(); vb = root.get("viewBox")
    sw = float(vb.split()[2]) if vb else float(root.attrib["width"])
    ns = {"svg":"http://www.w3.org/2000/svg"}
    g = root.find(".//svg:g", ns); fs = float(g.attrib.get("font-size", 12))
    rows = [(float(n.get("x","0")), float(n.get("y","0")), n.text or "") for n in root.findall(".//svg:text", ns)]
    return sw, fs, sorted(rows, key=lambda r:r[1])

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--config",type=Path,default=DEFAULT_CONFIG); ap.add_argument("--source",type=Path); ap.add_argument("--out",type=Path); ap.add_argument("--static",action="store_true"); o=ap.parse_args()
    c=load_config(o.config,{"terminal_user","display_name","portrait_source","portrait_output","portrait_animation"})
    src=o.source or project_path(c["portrait_source"]); out=o.out or project_path(c["portrait_output"])
    sw, sfs, rows=read_rows(src); loop=RevealLoop.from_config(c["portrait_animation"]); aw=CANVAS_W-PAD*2; scale=aw/sw; fs=sfs*scale; rh=sfs*scale
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace,Menlo,Consolas,monospace">',f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>','<style>.portrait-static{display:none}@media(prefers-reduced-motion:reduce){.portrait-motion{display:none}.portrait-static{display:inline}}</style>',f'<rect width="100%" height="100%" rx="12" fill="url(#bg)"/><rect x="0.5" y="0.5" width="839" height="874" rx="12" fill="none" stroke="{FRAME}"/><line x1="0" y1="{TITLEBAR_H}" x2="840" y2="{TITLEBAR_H}" stroke="{FRAME}"/>']
    for i,col in enumerate(["#ff5f56","#ffbd2e","#27c93f"]): parts.append(f'<circle cx="{PAD+i*16}" cy="15" r="5" fill="{col}"/>')
    parts.append(f'<text x="420" y="19" fill="{TITLE_TEXT}" font-size="12" text-anchor="middle">{html.escape(c["terminal_user"])}@github: ~$ ./portrait.sh</text>')
    static=[]; motion=[]
    for i,(x0,y0,line) in enumerate(rows):
        x=PAD+x0*scale; y=42+y0*scale; row_y=y-rh*.82; delay=i*float(c["portrait_animation"]["line_seconds"]); safe=html.escape(line)
        text=f'<text xml:space="preserve" x="{x:.1f}" y="{y:.1f}" fill="{INK}" font-size="{fs:.1f}">{safe}</text>'
        static.append(text)
        if not o.static:
            re,fs0,fe=loop.opacity_key_times(delay,float(c["portrait_animation"]["line_seconds"]))
            motion.append(f'<g class="portrait-motion" opacity="0"><animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;{re:.5f};{fs0:.5f};{fe:.5f};1" begin="{delay:.3f}s" dur="{loop.duration:.2f}s" repeatCount="indefinite"/><clipPath id="r{i}"><rect x="{PAD}" y="{row_y:.1f}" width="0" height="{rh:.1f}"><animate attributeName="width" values="0;{aw};{aw}" keyTimes="0;{re:.5f};1" begin="{delay:.3f}s" dur="{loop.duration:.2f}s" repeatCount="indefinite"/></rect></clipPath><g clip-path="url(#r{i})">{text}</g></g>')
    if o.static: parts.extend(static)
    else: parts.append('<g class="portrait-static">'+''.join(static)+'</g>'); parts.extend(motion)
    parts += [f'<line x1="0" y1="832" x2="840" y2="832" stroke="{FRAME}"/>',f'<text x="20" y="858" fill="{TITLE_TEXT}" font-size="13">{html.escape(c["terminal_user"])}@github:~$ whoami <tspan fill="{INK}">{html.escape(c["display_name"])}</tspan></text>','</svg>']
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(''.join(parts),encoding='utf-8')

if __name__=='__main__': main()
