#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, hashlib, json, math, random, statistics, sys, time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import can

CHANNEL='ssv2026-attack-10min-virtual-can'

def now_iso(): return datetime.now(timezone.utc).isoformat()
def sha256_file(path: Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()
def msg(arb:int,data:list[int]): return can.Message(arbitration_id=arb,is_extended_id=False,data=bytearray(data),timestamp=time.time())
def speed_payload(speed:int,rpm:int=1800,throttle:int=30,temp:int=86,fuel:int=75):
    return [speed&0xff,(speed>>8)&0xff,rpm&0xff,(rpm>>8)&0xff,throttle,temp,fuel,0]
def decode_speed(data_hex):
    b=bytes.fromhex(data_hex)
    return (b[0] | (b[1]<<8)) if len(b)>=2 else None

def send(bus, writer, raw_f, start, phase, m, note=''):
    bus.send(m, timeout=0.2)
    ts=time.time(); rel=ts-start; data=m.data.hex().upper()
    raw_f.write(f'({ts:.6f}) vcan_sim {m.arbitration_id:03X}#{data} phase={phase} note={note}\n')
    writer.writerow({'wall_ts':f'{ts:.6f}','relative_s':f'{rel:.6f}','phase':phase,'arbitration_id_hex':f'{m.arbitration_id:X}','dlc':len(m.data),'data_hex':data,'note':note})

def run_phase_normal(bus, writer, raw_f, start, duration, phase, rng, period=0.05):
    end=time.time()+duration; tick=0
    while time.time()<end:
        elapsed=time.time()-start
        speed=int(60+25*math.sin(elapsed/13)+8*math.sin(elapsed/3))
        rpm=int(1700+600*math.sin(elapsed/7))
        throttle=int(max(0,min(100,38+25*math.sin(elapsed/9))))
        send(bus,writer,raw_f,start,phase,msg(0x100,speed_payload(speed,rpm,throttle)), 'engine_cluster_state')
        send(bus,writer,raw_f,start,phase,msg(0x120,[0,0,0,0,0,0,0,0]), 'body_status')
        send(bus,writer,raw_f,start,phase,msg(0x188,[0,0,speed&0xff,(speed>>8)&0xff,0,0,0,0]), 'display_speed')
        if tick % 8 == 0: send(bus,writer,raw_f,start,phase,msg(0x300,[rng.randrange(256) for _ in range(8)]), 'background_noise')
        tick+=1; time.sleep(period)

def run_phase_spoof(bus, writer, raw_f, start, duration, rng, period=0.04):
    end=time.time()+duration; tick=0
    while time.time()<end:
        # Alternate malicious speed to make triage visible
        speed = 200 if tick % 4 else 180
        send(bus,writer,raw_f,start,'spoofing',msg(0x100,speed_payload(speed, rpm=4500, throttle=95, temp=91, fuel=70)), 'ATTACK fabricated speed/rpm/throttle')
        send(bus,writer,raw_f,start,'spoofing',msg(0x188,[0,0,speed&0xff,(speed>>8)&0xff,0xAA,0,0,0]), 'ATTACK display spoof')
        if tick % 10 == 0: send(bus,writer,raw_f,start,'spoofing',msg(0x120,[1,0,0,0,0,0,0,0]), 'ATTACK door/body spoof marker')
        tick+=1; time.sleep(period)

def run_phase_flood(bus, writer, raw_f, start, duration, rng, period=0.01):
    end=time.time()+duration
    while time.time()<end:
        arb=rng.randrange(0x001,0x7fe); payload=[rng.randrange(256) for _ in range(8)]
        send(bus,writer,raw_f,start,'flooding',msg(arb,payload),'ATTACK controlled flooding')
        time.sleep(period)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--duration', type=int, default=600)
    args=p.parse_args()
    out=Path(__file__).resolve().parent
    raw_path=out/'output_candump_annotated.log'; csv_path=out/'output_frames.csv'; plan_path=out/'input_attack_plan.json'
    findings_path=out/'findings.json'; report_path=out/'findings.md'; manifest_path=out/'manifest.json'
    # Fixed 600s profile: 180 baseline, 120 spoofing, 120 flooding, 180 recovery. Scale if duration != 600.
    scale=args.duration/600
    phases=[('baseline',180*scale),('spoofing',120*scale),('flooding',120*scale),('recovery',180*scale)]
    plan={'experiment_id':'006_10min_attack_software','scope':'Authorized 10-minute 100% software CAN attack simulation using python-can virtual backend; no physical vehicle or ECU.','channel':CHANNEL,'duration_s':args.duration,'phases':phases,'created_utc':now_iso(),'rates':{'normal_period_s':0.05,'spoof_period_s':0.04,'flood_period_s':0.01}}
    plan_path.write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    rng=random.Random(2026060310); start=time.time()
    with can.Bus(interface='virtual', channel=CHANNEL, receive_own_messages=True) as bus, raw_path.open('w',encoding='utf-8') as raw_f, csv_path.open('w',newline='',encoding='utf-8') as csv_f:
        writer=csv.DictWriter(csv_f, fieldnames=['wall_ts','relative_s','phase','arbitration_id_hex','dlc','data_hex','note']); writer.writeheader()
        run_phase_normal(bus,writer,raw_f,start,phases[0][1],'baseline',rng)
        run_phase_spoof(bus,writer,raw_f,start,phases[1][1],rng)
        run_phase_flood(bus,writer,raw_f,start,phases[2][1],rng)
        run_phase_normal(bus,writer,raw_f,start,phases[3][1],'recovery',rng)
    rows=[]
    with csv_path.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
    phase_counts=Counter(r['phase'] for r in rows); id_counts=Counter(r['arbitration_id_hex'] for r in rows)
    speeds=defaultdict(list)
    for r in rows:
        if r['arbitration_id_hex']=='100': speeds[r['phase']].append(decode_speed(r['data_hex']))
    duration=float(rows[-1]['relative_s']) if rows else 0
    findings={'experiment_id':'006_10min_attack_software','started_utc':plan['created_utc'],'ended_utc':now_iso(),'total_duration_s':duration,'total_frames':len(rows),'phase_counts':dict(phase_counts),'top_ids':id_counts.most_common(25),'speed_stats_by_phase_for_id_0x100':{k:{'count':len(v),'min':min(v),'max':max(v),'mean':round(statistics.mean(v),2),'stdev':round(statistics.pstdev(v),2)} for k,v in speeds.items() if v},'observations':['10-minute run produced longer baseline/spoofing/flooding/recovery windows for statistical analysis.','Spoofing alternated fabricated speed values around 180-200 km/h on ID 0x100 and mirrored display frames on ID 0x188.','Flooding used random arbitration IDs/payloads at a controlled 10 ms interval to create high-cardinality noise without excessive file size.','Recovery returned to normal periodic traffic, enabling before/during/after comparison.','Virtual backend validates software workflow and forensic evidence handling, not physical CAN electrical behavior.']}
    findings_path.write_text(json.dumps(findings,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    report=f'''# Findings — Experiment 006: 10-Minute Software CAN Attack

## Escopo
Authorized, 100% software execution using the `python-can` virtual backend. No vehicle, physical ECU, or external network was involved.

## Duration and phases
- Total duration: {duration:.2f} s
- Frames totais: {len(rows)}
- Frames por fase: `{dict(phase_counts)}`

## Decoded speed on ID 0x100
```json
{json.dumps(findings['speed_stats_by_phase_for_id_0x100'],indent=2,ensure_ascii=False)}
```

## IDs mais frequentes
`{id_counts.most_common(15)}`

## Findings
1. Baseline and recovery maintained normal periodic traffic on IDs 0x100, 0x120, 0x188, and 0x300.
2. Spoofing fabricated speed/RPM/throttle values, concentrating ID 0x100 around 180–200 km/h.
3. Flooding generated high arbitration ID cardinality, useful for noise measurement and forensic triage.
4. The artifacts support temporal statistical analysis and hash-based chain-of-custody validation.

## Limitation
The virtual backend does not model the CAN physical layer, electrical arbitration, bus termination, transceiver behavior, or real bus errors.
'''
    report_path.write_text(report,encoding='utf-8')
    manifest={'schema':'software-can-testbed.attack-run.v1','experiment_id':'006_10min_attack_software','created_utc':now_iso(),'python':sys.version,'python_can_version':can.__version__,'files':{}}
    for path in [plan_path, raw_path, csv_path, findings_path, report_path]: manifest['files'][path.name]={'sha256':sha256_file(path),'bytes':path.stat().st_size}
    manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(findings,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
