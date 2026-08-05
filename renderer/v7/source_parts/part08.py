if not qc['narration']['pass'] or not qc['interior_asset_audit_pass'] or not qc['interior_exposure_pass'] or not qc['aspect_ratio_policy']['pass'] or not qc['transitions']['pass'] or not qc['non_rank_media']['pass']: qc['all_pass']=False
(OUT/'V7_QC_REPORT.json').write_text(json.dumps(qc,indent=2),encoding='utf-8')
(OUT/'caption-timing-audit.json').write_text(json.dumps([dict(cue=i,start=round(a,3),end=round(b,3),text=txt,sync_basis='original continuous V5 narration + deterministic global time warp') for i,a,b,txt in MAPPED_CUES],indent=2),encoding='utf-8')
(OUT/'scene-and-crop-manifest.json').write_text(json.dumps({'scene_boundaries':bounds,'scene_spans':spans,'transition_seconds':TRANS,'transition_type':'opaque wipeleft','transparent_ui_overlap_count':0,'media_policy':'cover crop only','rank_exterior_crop':'V6 exact-aircraft media window 886x588 @ x20 y350','non_rank_source_policy':'clean source-only compositions; no prior rendered frames','minimum_full_opacity_interior_seconds':1.65,'all_wide_assets':'force_original_aspect_ratio=increase then crop'},indent=2),encoding='utf-8')

print(json.dumps(qc, indent=2))
if not qc['all_pass']:
    raise SystemExit('QC failed')
print(json.dumps({'final':str(final),'duration':TOTAL,'qc':qc['all_pass']},indent=2))
