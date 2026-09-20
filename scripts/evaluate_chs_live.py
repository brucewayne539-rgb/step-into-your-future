#!/usr/bin/env python3
"""Opt-in paid API evaluation. Never loaded by the application or unit tests.

Run on a private test service with OPENAI_API_KEY configured:
  python scripts/evaluate_chs_live.py --scope priority --output chs-live-review
  python scripts/evaluate_chs_live.py --scope all --output chs-live-review-all
The HTML packet must receive educational review; passing automation is not release approval.
"""
import argparse,html,json,sys,os,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from chs_roadmap import generate_chs_roadmap
from app import CAREERS,load_key

PRIORITY=['Neurosurgeon','Nurse Practitioner','Cybersecurity Specialist']

def acceptance_checks(career,grade,result):
    chs=result['chs'];cards=sum([chs[k] for k in ['primary_course_details','supporting_course_details','future_course_details']],[])
    current=[c for c in cards if c['planned_grade']==max(9,grade)]
    checks=[]
    if career in {'Neurosurgeon','Nurse Practitioner'} and not any(c['course_id'] in {'CHS-040','CHS-047','CHS-048','CHS-049','CHS-050','CHS-051','CHS-053'} for c in current):
        checks.append('No direct biomedical/healthcare starting option for this grade.')
    if career=='Cybersecurity Specialist' and not any(c['course_id'] in {'CHS-129','CHS-131','CHS-132','CHS-133','CHS-134','CHS-135'} for c in current):
        checks.append('No computing/security starting option for this grade.')
    if grade==12 and chs['future_course_details']:checks.append('Future high-school years shown for a senior.')
    if len({(s[0],s[1]) for s in result['steps']})!=len(result['steps']):checks.append('Duplicate postsecondary stages.')
    return checks

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scope',choices=['priority','all'],default='priority')
    p.add_argument('--output',default='chs-live-review')
    p.add_argument('--repeat',type=int,default=1,choices=[1,2,3])
    args=p.parse_args();key=load_key()
    if not key:
        print('NOT RUN: OPENAI_API_KEY is missing. No live quality claim can be made.',file=sys.stderr);return 2
    careers=PRIORITY if args.scope=='priority' else list(CAREERS)
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    count=len(careers)*5*args.repeat
    print(f'Running {count} real roadmaps, up to {2*count} paid text requests. No portrait calls.',flush=True)
    results=[]
    for repeat in range(args.repeat):
        for career in careers:
            for grade in range(8,13):
                started=time.monotonic();row={'career':career,'grade':grade,'repeat':repeat+1}
                try:
                    result=generate_chs_roadmap(career,grade,api_key=key)
                    issues=acceptance_checks(career,grade,result)
                    row.update(result=result,issues=issues,automatic_status='FAIL' if issues else 'PASS')
                except Exception as e:
                    # Safe application errors only; never write key/provider internals.
                    row.update(automatic_status='FAIL',issues=[str(e) if type(e).__name__=='RoadmapUnavailable' else type(e).__name__])
                row['seconds']=round(time.monotonic()-started,1);results.append(row)
                (output/'results.json').write_text(json.dumps({'live_api':True,'educational_signoff':'PENDING','model':os.getenv('ROADMAP_MODEL','gpt-4.1'),'results':results},indent=2,ensure_ascii=False))
                print(f"{len(results)}/{count} {row['automatic_status']} grade {grade} {career}",flush=True)
    esc=html.escape
    sections=[]
    for row in results:
        section=f"<section><h2>{esc(row['career'])} · Grade {row['grade']} · {row['automatic_status']}</h2>"
        if 'result' in row:
            result=row['result'];c=result['chs'];section+='<p>'+esc(result['summary'])+'</p><p>'+esc(c['grade_note'])+'</p>'
            for title,field in [('Starting options','primary_course_details'),('Supporting options','supporting_course_details'),('Later options','future_course_details')]:
                section+='<h3>'+title+'</h3>'
                for x in c[field]:section+=f"<article><b>{esc(x['name'])}</b> · planned grade {x['planned_grade']} · catalog p. {x['page']}<p>{esc(x['why'])}</p><p>Entry: {esc(x['prerequisite'])}</p><p>{esc(x['planning_note'])}</p></article>"
            section+='<h3>Beyond high school</h3>'+''.join('<p><b>'+esc(t)+'</b> '+esc(d)+'</p>' for t,d in result['steps'])
            for field in ['experience','good','next','reflection']:section+='<p>'+esc(c[field])+'</p>'
        section+=''.join('<p class="fail">'+esc(x)+'</p>' for x in row['issues'])
        sections.append(section+'<p>Educational review: ______  Reviewer/date: ______</p></section>')
    intro='''<!doctype html><meta charset="utf-8"><title>CHS live educational review</title><style>body{font:16px/1.5 Arial;max-width:1000px;margin:35px auto;color:#18354c}section{border-top:4px solid #235980;margin:35px 0;padding-top:15px}article{border-left:3px solid #85b7cb;padding:8px 15px;margin:12px 0;background:#f3f8fa}.fail{color:#a12525}@media print{section{break-before:page}}</style><h1>Actual CHS AI roadmaps — educational review required</h1><p>Check relevance, strongest available courses, exact entry requirements, feasible progression, late-entry options, truthful training routes, useful experiences and student readability. Every serious error blocks release. Automation and a second model review are not human educational signoff.</p>'''
    (output/'review.html').write_text(intro+''.join(sections),encoding='utf-8')
    failed=sum(r['automatic_status']=='FAIL' for r in results)
    print(f'{len(results)-failed}/{len(results)} passed automatic checks. Human educational review remains PENDING. Review {output / "review.html"}')
    return 1 if failed else 0

if __name__=='__main__':sys.exit(main())
