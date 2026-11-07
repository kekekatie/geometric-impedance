"""Log command, environment-independent argv, timing and exit status per phase."""
import sys, subprocess, datetime, json
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
phase=sys.argv[1]
logs=HERE/'logs';logs.mkdir(exist_ok=True)
cmd=[sys.executable,'-u',str(HERE/'src/run.py'),phase]
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
with (logs/(phase+'.log')).open('w',encoding='utf-8') as f:
    p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
record=dict(argv=cmd,start_utc=start,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=p.returncode)
(logs/(phase+'-execution.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record),flush=True)
sys.exit(p.returncode)
