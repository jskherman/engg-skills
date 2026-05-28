#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations
import argparse, json, sys, urllib.parse, urllib.request
from pathlib import Path
COMMON_ROOT = Path(__file__).resolve().parents[2] / "engg-skills-common"; sys.path.insert(0, str(COMMON_ROOT))
from engg_skills_common.io import result_envelope, write_json
from engg_skills_common.notices import license_notice_for, write_license_notification

SKILL = "literature-search-engineering"
SKILL_DIR = Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description='Search OpenAlex works metadata'); p.add_argument('--query', required=True); p.add_argument('--limit', type=int, default=10); p.add_argument('--mailto'); p.add_argument('--output', required=True); a=p.parse_args()
    write_license_notification(
        skill_dir=SKILL_DIR,
        skill_name=SKILL,
        terms_urls=["https://docs.openalex.org/", "https://api.crossref.org/"],
        extra_notes="Review each API's terms, rate limits, and attribution requirements before reuse.",
    )
    try:
        params={'search':a.query,'per-page':str(min(max(a.limit,1),50))};
        if a.mailto: params['mailto']=a.mailto
        url='https://api.openalex.org/works?'+urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=30) as r: raw=json.load(r)
        items=[{'title':w.get('title'),'year':w.get('publication_year'),'doi':w.get('doi'),'openalex_id':w.get('id'),'cited_by_count':w.get('cited_by_count')} for w in raw.get('results',[])]
        data=result_envelope(skill=SKILL, inputs=vars(a), results={'query_url':url,'items':items}, sources=['https://docs.openalex.org/'])
        data["source_notice"] = license_notice_for(SKILL)
        path=write_json(data, a.output); print(f'Success. JSON written to: {path}'); return 0
    except Exception as e:
        write_json(result_envelope(skill='literature-search-engineering', inputs=vars(a), results={'error':str(e)}, ok=False), a.output); print(f'Error. JSON written to: {a.output}', file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())
