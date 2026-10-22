from pathlib import Path
import json
p=Path(__file__).resolve().parent/'choice-tracking'
r=json.loads((p/'inventory.json').read_text())
summary=[]
for i,a in enumerate(r):
    for e in a['events']:
        site=e['site']; s=e['slice']; first=e['first_observed_open_before_slice']
        own=[(row['slice'],x) for row in a['records'] if row['slice']<=s for x in row['frontier'] if x['site']==site]
        other=[dict(slice=row['slice'],count=x['count'],same_options=x['options']==e['options']) for row in r[1-i]['records'] for x in row['frontier'] if x['site']==site]
        summary.append(dict(continuation=a['continuation'],slice=s,first_open=first,continuously_open_until_selected=all(any(x['site']==site and x['count']>1 for x in row['frontier']) for row in a['records'][first-1:s]),same_options_since_first_open=all(x['options']==e['options'] for ss,x in own if ss>=first),other_history_observations=other))
(p/'event-summary.json').write_text(json.dumps(summary,indent=2))
for x in summary:
    print({k:v for k,v in x.items() if k!='other_history_observations'})
    print('Other history:',x['other_history_observations'])
