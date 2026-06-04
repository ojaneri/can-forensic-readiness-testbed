#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, statistics, time
from datetime import datetime, timezone
from pathlib import Path
import can
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SRC=ROOT/'dataset/experiments/008_external_icsim_replay/frames_normalized.csv'
CSV=OUT/'frames_normalized.csv'; RAW=OUT/'python_can_icsim_replay.log'; SUMMARY=OUT/'summary.json'; FINDINGS=OUT/'findings.md'
CHANNEL='oc_vcan_012'
rows_in=[]
with SRC.open() as f:
    for r in csv.DictReader(f): rows_in.append(r)
# infer timestamp col robustly
for cand in ['relative_time_s','timestamp_s','timestamp','time_s','relative_timestamp_s','timestamp_epoch_s']:
    if cand in rows_in[0]: ts_col=cand; break
else: ts_col=list(rows_in[0].keys())[0]
# infer id/data cols
id_col='arbitration_id' if 'arbitration_id' in rows_in[0] else 'can_id'
data_col='payload_hex' if 'payload_hex' in rows_in[0] else ('data_hex' if 'data_hex' in rows_in[0] else 'data')
base_ts=float(rows_in[0][ts_col])
start=time.monotonic(); out=[]; seq=0
bus=can.Bus(interface='virtual', channel=CHANNEL, receive_own_messages=True)
with RAW.open('w') as raw:
    for r in rows_in:
        target=float(r[ts_col])-base_ts
        sleep_for=start+target-time.monotonic()
        if sleep_for>0: time.sleep(sleep_for)
        aid_s=str(r[id_col]).strip().replace('0x','').replace('0X','')
        aid=int(aid_s,16)
        hx=str(r[data_col]).replace(' ','').replace('#','')
        data=bytes.fromhex(hx[:16].ljust(16,'0'))
        send=time.monotonic(); bus.send(can.Message(arbitration_id=aid,data=data,is_extended_id=False), timeout=.1)
        rx=bus.recv(timeout=.05); recv=time.monotonic()
        if rx is None: continue
        rel=recv-start
        row={'timestamp_s':f'{rel:.6f}','utc_iso':datetime.now(timezone.utc).isoformat(),'arbitration_id':f'{rx.arbitration_id:X}','dlc':str(rx.dlc),'data_hex':' '.join(f'{b:02X}' for b in rx.data),'label':'python_can_icsim_replay','source':'012_python_can_icsim_replay','send_to_recv_latency_s':f'{recv-send:.6f}','note':'external_icsim_trace_replayed_on_python_can_virtual_bus'}
        out.append(row); seq+=1
        raw.write(f'({rel:.6f}) {CHANNEL} {rx.arbitration_id:X}#'+''.join(f'{b:02X}' for b in rx.data)+'\n')
try: bus.shutdown()
except Exception: pass
with CSV.open('w', newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
ts=[float(r['timestamp_s']) for r in out]; inter=[b-a for a,b in zip(ts,ts[1:])]; lat=[float(r['send_to_recv_latency_s']) for r in out]
counts={}
for r in out: counts[r['arbitration_id']]=counts.get(r['arbitration_id'],0)+1
summary={'experiment_id':'012_python_can_icsim_replay','created_utc':datetime.now(timezone.utc).isoformat(),'purpose':'Replay external ICSim normalized trace through python-can virtual bus preserving source inter-arrival timing; not IDS benchmark or vehicle validation.','base_experiment':'008_external_icsim_replay','python_can_version':can.__version__,'channel':CHANNEL,'input_frames':len(rows_in),'replayed_frames':len(out),'measured_duration_s':round(ts[-1]-ts[0],6),'unique_arbitration_ids':len(counts),'id_counts_top20':dict(sorted(counts.items(), key=lambda kv:kv[1], reverse=True)[:20]),'inter_arrival_s':{'count':len(inter),'min':round(min(inter),6),'max':round(max(inter),6),'mean':round(statistics.mean(inter),6),'median':round(statistics.median(inter),6),'stdev':round(statistics.pstdev(inter),6),'negative_values':sum(1 for x in inter if x<0)},'send_to_recv_latency_s':{'count':len(lat),'min':round(min(lat),6),'max':round(max(lat),6),'mean':round(statistics.mean(lat),6),'median':round(statistics.median(lat),6),'stdev':round(statistics.pstdev(lat),6)},'boundary':'External ICSim sample replayed on python-can virtual bus only. No live CAN adapter, ECU, or vehicle.'}
SUMMARY.write_text(json.dumps(summary,indent=2)+'\n')
FINDINGS.write_text(f"""# Experiment 012 — python-can ICSim replay\n\n- Base: Experiment 008 normalized ICSim trace\n- Input frames: {len(rows_in)}\n- Replayed frames: {len(out)}\n- Duration: {summary['measured_duration_s']} s\n- Unique IDs: {summary['unique_arbitration_ids']}\n- Mean inter-arrival: {summary['inter_arrival_s']['mean']} s\n- Negative inter-arrival values: {summary['inter_arrival_s']['negative_values']}\n- Mean send→recv latency: {summary['send_to_recv_latency_s']['mean']} s\n\nBoundary: virtual bus replay only; no physical CAN or IDS benchmark claim.\n""")
def sha(p):
 h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
files=['run_python_can_icsim_replay.py','frames_normalized.csv','python_can_icsim_replay.log','summary.json','findings.md']
(OUT/'manifest.json').write_text(json.dumps({'experiment_id':'012_python_can_icsim_replay','files':{n:{'sha256':sha(OUT/n),'bytes':(OUT/n).stat().st_size} for n in files}},indent=2)+'\n')
