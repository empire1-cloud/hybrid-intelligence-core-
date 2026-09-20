"""Compose a self-contained HTML5 canvas game from deterministic manifests."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

def compose_web(spec: Any, verification: Dict[str, Any], assets: list, audio: list, root: Path) -> Dict[str, Any]:
    web=root/"web"; web.mkdir(parents=True, exist_ok=True)
    manifest={"name":spec.name,"version":"0.1.0","game_type":spec.game_type,"theme":spec.theme,"verification":verification,"assets":assets,"audio":audio}
    (web/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    js='''const c=document.querySelector("canvas"),x=c.getContext("2d"); let fish=[],score=0; function spawn(){fish=[]; for(let i=0;i<8;i++)fish.push({x:80+i*145,y:180+(i%3)*110,r:35+i%3*8,v:1+(i%4)});} function draw(){x.clearRect(0,0,c.width,c.height); x.fillStyle="#071018";x.fillRect(0,0,c.width,c.height); x.fillStyle="#f4d35e";x.font="24px sans-serif";x.fillText("GENESIS ENGINE • PLAYABLE WEB BUILD",24,40);x.fillText("Score: "+score,24,72); for(const f of fish){x.fillStyle="#48bfe3";x.beginPath();x.ellipse(f.x,f.y,f.r,f.r*.55,0,0,7);x.fill();x.fillStyle="#071018";x.beginPath();x.arc(f.x-12,f.y-8,4,0,7);x.fill();f.x+=f.v;if(f.x>c.width+60)f.x=-60;}requestAnimationFrame(draw)} c.onclick=e=>{for(let i=fish.length-1;i>=0;i--){let f=fish[i],d=Math.hypot(e.offsetX-f.x,e.offsetY-f.y);if(d<f.r){score+=Math.round(f.r/5);fish.splice(i,1);break;}}if(!fish.length)spawn()}; spawn();draw();'''
    html=f'''<!doctype html><html><head><meta charset="utf-8"><title>{spec.name}</title><style>html,body{{margin:0;background:#05080c;color:#fff;font-family:system-ui}}canvas{{display:block;width:100vw;height:100vh;cursor:crosshair}}</style></head><body><canvas width="{spec.width}" height="{spec.height}"></canvas><script>{js}</script></body></html>'''
    (web/"index.html").write_text(html,encoding="utf-8")
    return {"format":"html5","entrypoint":"web/index.html","files":["web/index.html","web/manifest.json"],"status":"playable"}
