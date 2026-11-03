"""Record exact replay identifiers, endpoint geometry hashes and final edge identities."""
from audit_common import *
def main():
    records=[]
    for w,si in S.B_JAMS:
        jam=load(f'jam-{w}-{si}.pkl');res=load(f'growth-{w}-{si}.pkl');P=S.L.Patch(res['full']);fr=P.frontier();current={S.ekey(e[0],e[1]) for e in fr};blocked={S.ekey(e[0],e[1]) for e in fr if not S.D.candidates(P,*e[:3])};labels={frozenset(tuple(v) for v in e) for e in res['scars']};enc=lambda edges:sorted(sorted(e) for e in edges)
        records.append(dict(case=f'w{w}-B-s{si}',world=w,stream_index=si,stream=res['stream'],option_index=1,option_shape=int(res['B'][0]),jam_step=jam['jam_step'],final_step=res['final_step'],fork_geometry_hash=tilehash(res['Sstar']),jam_full_hash=tilehash(jam['full']),jam_band_hash=tilehash(jam['band']),final_full_hash=tilehash(res['full']),final_band_hash=tilehash(res['band']),final_cumulative_labels=enc(labels),final_current_frontier=enc(current),final_current_blocked=enc(blocked),final_unlabelled_blocked=enc(blocked-labels),final_disappeared_labels=enc(labels-current)))
    dump('replay_manifest.json',records);print('Replay manifest exported.',flush=True)
if __name__=='__main__':main()
