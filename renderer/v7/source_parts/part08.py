if not qc['narration']['pass'] or not qc['interior_asset_audit_pass'] or not qc['aspect_ratio_policy']['pass'] or not qc['transitions']['pass']: qc['all_pass']=False
(OUT/'V7_QC_REPORT.json').write_text(json.dumps(qc,indent=2),encoding='utf-8')
(OUT/'caption-timing-audit.json').write_text(json.dumps([dict(cue=i,start=round(a,3),end=round(b,3),text=txt,sync_basis='original continuous V5 narration + deterministic global time warp') for i,a,b,txt in MAPPED_CUES],indent=2),encoding='utf-8')
(OUT/'scene-and-crop-manifest.json').write_text(json.dumps({'scene_boundaries':bounds,'scene_spans':spans,'transition_seconds':TRANS,'media_policy':'cover crop only','source_crop':'V5 media window 885x500 @ x20 y395','rank_exterior_crop':'V6 exact-aircraft media window 886x588 @ x20 y350','all_wide_assets':'force_original_aspect_ratio=increase then crop'},indent=2),encoding='utf-8')

if not qc['all_pass']:
    raise SystemExit('QC failed')
print(json.dumps({'final':str(final),'duration':TOTAL,'qc':qc['all_pass']},indent=2))
