#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, random, statistics, time
from datetime import datetime, timezone
from pathlib import Path
import can
OUT=Path(__file__).resolve().parent
CSV=OUT/'frames_normalized.csv'; RAW=OUT/'python_can_virtual.log'; SUMMARY=OUT/'summary.json'; FINDINGS=OUT/'findings.md'
SEED=2026060412; DURATION_S=30.0
random.seed(SEED)
CHANNEL='oc_vcan_011'
IDS=[0x100,0x120,0x188,0x300]
PERIODS={0x100:.050,0x120:.070,0x188:.050,0x300:.250}
next_due={}
rows=[]; received=[]
def data_for(aid, seq):
    if aid==0x100:
        speed=58+random.randrange(18); return [speed,0,0,0,0,0,0,seq&255]
    if aid==0x120:
        rpm=1400+random.randrange(500); return [(rpm>>8)&255,rpm&255,0,0,0,0,0,seq&255]
    if aid==0x188:
        return [0,0,0,0,0,0,0,seq&255]
    return [random.randrange(256) for _ in range(8)]
start_mono=time.monotonic(); start_utc=datetime.now(timezone.utc).isoformat()
for aid in IDS: next_due[aid]=start_mono
seq=0
# python-can virtual bus: preserve_sent_messages lets same bus receive sent msgs
bus=can.Bus(interface='virtual', channel=CHANNEL, receive_own_messages=True)
with RAW.open('w') as raw:
    while True:
        now=time.monotonic()
        if now-start_mono>=DURATION_S: break
        aid=min(next_due, key=next_due.get)
        sleep_for=next_due[aid]-time.monotonic()
        if sleep_for>0: time.sleep(sleep_for)
        send_mono=time.monotonic()
        msg=can.Message(arbitration_id=aid, data=data_for(aid,seq), is_extended_id=False)
        bus.send(msg, timeout=0.1)
        rx=bus.recv(timeout=0.05)
        recv_mono=time.monotonic()
        if rx is None: continue
        ts_rel=recv_mono-start_mono
        data_hex=' '.join(f'{b:02X}' for b in rx.data)
        row={
          'timestamp_s':f'{ts_rel:.6f}', 'utc_iso':datetime.now(timezone.utc).isoformat(),
          'arbitration_id':f'{rx.arbitration_id:X}', 'dlc':str(rx.dlc), 'data_hex':data_hex,
          'label':'python_can_virtual_baseline','source':'011_python_can_virtual_bus',
          'send_to_recv_latency_s':f'{recv_mono-send_mono:.6f}',
          'note':'python_can_virtual_bus_no_vehicle_no_adapter'
        }
        rows.append(row); received.append(rx)
        raw.write(f'({ts_rel:.6f}) {CHANNEL} {rx.arbitration_id:X}#'+''.join(f'{b:02X}' for b in rx.data)+'\n')
        seq+=1; next_due[aid]+=PERIODS[aid]
try: bus.shutdown()
except Exception: pass
with CSV.open('w', newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
ts=[float(r['timestamp_s']) for r in rows]; inter=[b-a for a,b in zip(ts,ts[1:])]
lat=[float(r['send_to_recv_latency_s']) for r in rows]
counts={}
for r in rows: counts[r['arbitration_id']]=counts.get(r['arbitration_id'],0)+1
summary={
 'experiment_id':'011_python_can_virtual_bus','created_utc':datetime.now(timezone.utc).isoformat(),
 'purpose':'python-can virtual bus wall-clock capture after installing python-can; validates tool-backed virtual CAN workflow, not physical CAN.',
 'python_can_version':can.__version__,'channel':CHANNEL,'seed':SEED,'requested_duration_s':DURATION_S,
 'measured_duration_s':round(ts[-1]-ts[0],6),'total_frames':len(rows),'unique_arbitration_ids':len(counts),'id_counts':counts,
 'inter_arrival_s':{'count':len(inter),'min':round(min(inter),6),'max':round(max(inter),6),'mean':round(statistics.mean(inter),6),'median':round(statistics.median(inter),6),'stdev':round(statistics.pstdev(inter),6),'negative_values':sum(1 for x in inter if x<0)},
 'send_to_recv_latency_s':{'count':len(lat),'min':round(min(lat),6),'max':round(max(lat),6),'mean':round(statistics.mean(lat),6),'median':round(statistics.median(lat),6),'stdev':round(statistics.pstdev(lat),6)},
 'boundary':'Uses python-can virtual bus only. No physical CAN adapter, ECU, or vehicle is involved.'
}
SUMMARY.write_text(json.dumps(summary,indent=2)+'\n')
FINDINGS.write_text(f"""# Experiment 011 — python-can virtual bus\n\n- python-can: {can.__version__}\n- Total frames: {summary['total_frames']}\n- Duration: {summary['measured_duration_s']} s\n- Unique IDs: {summary['unique_arbitration_ids']}\n- Mean inter-arrival: {summary['inter_arrival_s']['mean']} s\n- Negative inter-arrival values: {summary['inter_arrival_s']['negative_values']}\n- Mean send→recv latency: {summary['send_to_recv_latency_s']['mean']} s\n\nBoundary: virtual bus only; no physical CAN fidelity claim.\n""")
def sha(p):
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()
files=['run_python_can_virtual_bus.py','frames_normalized.csv','python_can_virtual.log','summary.json','findings.md']
(OUT/'manifest.json').write_text(json.dumps({'experiment_id':'011_python_can_virtual_bus','files':{n:{'sha256':sha(OUT/n),'bytes':(OUT/n).stat().st_size} for n in files}},indent=2)+'\n')
