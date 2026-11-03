"""Create corrected tables from completed audit outputs, without further searches."""
import csv,platform
from audit_common import *
def main():
    sched=json.loads((RESULTS/'scheduler_verification.json').read_text());reads=json.loads((RESULTS/'readout_verification.json').read_text());sens=json.loads((RESULTS/'sensitivity.json').read_text());bounds=json.loads((RESULTS/'boundary_intersections.json').read_text());assert sched['complete'] and reads['complete'] and sens['complete']
    rows=[];step0=[]
    for case,read in zip(sched['cases'],reads['cases']):
        assert case['case']==read['case'];final=case['checkpoints'][-1];tag=case['case'];w=int(tag.split('-')[0][1:]);si=int(tag.split('-')[-1][1:]);st=load(f'growth-{w}-{si}.pkl');assert S.L.Patch(st['Sstar']).legal(st['B']);step0.append(tag)
        row=dict(case=tag,stream=case['stream'],jam_step=case['jam_step'],final_step=case['final_step'],baseline_jam_full_tiles=case['baseline_jam_full_tiles'],first_scar_step_added=case['first_scar_step_additions'],later_added=case['historical_added_after_scar_step'],added_from_frozen_jam=case['added_from_frozen_jam'],final_full_tiles=case['final_full_tiles'],cumulative_labels=final['cumulative_scar']['edges'],labelled_current=final['labelled_current']['edges'],current_blocked=final['current_zero_candidate']['edges'],current_blocked_components=final['current_zero_candidate']['vertex_connected_components'],current_blocked_span=final['current_zero_candidate']['span_radians'],new_unlabelled_blocked=final['unlabelled_current_zero'],labelled_extendable=final['labelled_extendable'],labelled_disappeared=final['labelled_disappeared'],B_in_jam_band=case['B_in_jam_band'],B_departure_step=case['choice_departure_step'],B_in_final_band=case['B_in_final_band'],B_in_final_archive=case['B_in_final_archive'])
        for checkpoint in ['jam','final']:
            best=read['checkpoints'][checkpoint]['largest_found'];bound=next(x for x in bounds if x['case']==tag and x['checkpoint']==checkpoint)
            row.update({checkpoint+'_selected_tiles':best['n_tiles'],checkpoint+'_selected_fraction':best['fraction'],checkpoint+'_reader_selection':best['outcome'],checkpoint+'_A_intersection':bound['numerical_dimension'],checkpoint+'_B_in_selected':best['B_in_subset']})
        rows.append(row)
    dump('corrected_summary.json',rows)
    with (RESULTS/'corrected_summary.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    split=collections.Counter()
    for g in sens['main_grid']:
        for r in g['windows']:
            if r['outcome']=='empty_incompatible':
                m=r['feasibility']['margin'];split['negative_margin' if m is not None and m < -1e-9 else 'boundary_margin' if m is not None and abs(m)<=1e-9 else 'positive_margin_no_birth_hypothesis']=split['negative_margin' if m is not None and m < -1e-9 else 'boundary_margin' if m is not None and abs(m)<=1e-9 else 'positive_margin_no_birth_hypothesis']+1
    dump('audit_summary.json',dict(scheduled_additions_checked=sum(c['total_additions_checked'] for c in sched['cases']),step0_B_legality_passed=step0,final_vertex_stars_checked=sum(c['legality']['vertices'] for c in sched['cases']),max_numerical_triangle_intersection_area=max(c['legality']['overlap']['max_intersection_area'] for c in sched['cases']),grid_counts={k:sens['summary']['main_counts'].get(k,0) for k in ['A','B','ambiguous','empty_incompatible','reconstruction_failure']},reader_empty_category_split=dict(split),A_boundary_intersections=collections.Counter(x['numerical_dimension'] for x in bounds),environment=dict(python=sys.version,executable=sys.executable,platform=platform.platform(),numpy=np.__version__),all_frozen_histories_match=all(c['prejam_all_rng_and_geometry_equal'] for c in sched['cases']),all_steps_make_progress=all(not c['zero_placement_steps'] for c in sched['cases'])))
    print('Corrected tables and audit summary written.',flush=True)
if __name__=='__main__':main()
