#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations
import argparse, json, sys, urllib.parse, urllib.request
from pathlib import Path
COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg_skills_common"; sys.path.insert(0, str(COMMON_ROOT))
from engg_skills_common.io import result_envelope, write_json

def main():
    p=argparse.ArgumentParser(description='Search Crossref works metadata'); p.add_argument('--query', required=True); p.add_argument('--limit', type=int, default=10); p.add_argument('--mailto'); p.add_argument('--output', required=True); a=p.parse_args()
    try:
        params={'query':a.query,'rows':str(min(max(a.limit,1),50))}; url='https://api.crossref.org/works?'+urllib.parse.urlencode(params)
        req=urllib.request.Request(url, headers={'User-Agent': f'engg-skills/0.1 ({a.mailto or "mailto optional"})'})
        with urllib.request.urlopen(req, timeout=30) as r: raw=json.load(r)
        items=[{'title':(w.get('title') or [None])[0],'year':(((w.get('issued') or {}).get('date-parts') or [[None]])[0][0]),'doi':w.get('DOI'),'url':w.get('URL'),'container_title':(w.get('container-title') or [None])[0]} for w in raw.get('message',{}).get('items',[])]
        path=write_json(result_envelope(skill='literature_search_engineering', inputs=vars(a), results={'query_url':url,'items':items}, sources=['https://www.crossref.org/documentation/retrieve-metadata/rest-api/']), a.output); print(f'Success. JSON written to: {path}'); return 0
    except Exception as e:
        write_json(result_envelope(skill='literature_search_engineering', inputs=vars(a), results={'error':str(e)}, ok=False), a.output); print(f'Error. JSON written to: {a.output}', file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())
