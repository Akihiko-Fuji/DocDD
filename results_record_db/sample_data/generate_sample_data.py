import csv
import random
from datetime import date, datetime, time, timedelta

random.seed(42)

PRODUCTS = [
    ("RS-90X180-WH", (130, 155), (200, 260), (290, 360), 900, 1800),
    ("RS-120X200-GY", (140, 165), (210, 275), (310, 380), 1200, 2000),
    ("VB-50-80X150-IV", (160, 195), (260, 320), (360, 430), 800, 1500),
    ("VT-80X200-LG", (185, 225), (310, 380), (420, 500), 800, 2000),
    ("RS-180X220-BK", (200, 240), (340, 420), (460, 540), 1800, 2200),
]
PDICT = {p[0]: p for p in PRODUCTS}

PLAN = {
    date(2026, 1, 5): 18, date(2026, 1, 6): 25, date(2026, 1, 7): 20, date(2026, 1, 8): 13, date(2026, 1, 9): 19,
    date(2026, 1, 13): 24, date(2026, 1, 14): 21, date(2026, 1, 15): 18, date(2026, 1, 16): 12,
    date(2026, 1, 19): 20, date(2026, 1, 20): 22, date(2026, 1, 21): 26, date(2026, 1, 22): 19, date(2026, 1, 23): 18,
    date(2026, 1, 26): 21, date(2026, 1, 27): 25, date(2026, 1, 28): 20, date(2026, 1, 29): 19, date(2026, 1, 30): 13,
}
DAYS = list(PLAN.keys())
KIMURA_BAD = {date(2026, 1, 7), date(2026, 1, 13), date(2026, 1, 20), date(2026, 1, 28)}

def dt(d, h=8, m=0, s=0):
    return datetime.combine(d, time(h, m, s))

def dur(rng):
    return timedelta(seconds=random.randint(*rng))

def wait1(t0, plus=0):
    if t0.hour < 10: base = (60 + plus, 120 + plus)
    elif t0.hour < 12: base = (30 + plus, 60 + plus)
    elif t0.hour < 15: base = (15 + plus, 30 + plus)
    else: base = (10 + plus, 20 + plus)
    return timedelta(minutes=random.randint(*base))

def wait2():
    return timedelta(minutes=random.randint(10, 40))

def pick_products(n):
    seq=[]
    cycle=[0,1,2,3,4,1,2,0,4,3]
    for i in range(n): seq.append(PRODUCTS[cycle[i%len(cycle)]][0])
    return seq

def build():
    orders=[]
    order_no=10001
    kpi2_low_days=0
    ext_wait_plus=0
    while True:
        orders.clear()
        order_no=10001
        for d in DAYS:
            n=PLAN[d]
            prods=pick_products(n)
            tanaka_target = 5 + (0 if d.day<=9 else 1 if d.day<=16 else 2 if d.day<=23 else 3)
            tanaka_target += 0 if d.day%2 else 1
            tanaka_target = min(max(tanaka_target,5),9)
            yamada_target = n - tanaka_target
            if yamada_target < 10:
                yamada_target = 10
                tanaka_target = n - 10
            if yamada_target > 12:
                yamada_target = 12
                tanaka_target = n - 12
            ext_kimura = 12 if n >= 24 else 10
            if d in KIMURA_BAD: ext_kimura = 6 if n >= 18 else 5
            ext_sato = n - ext_kimura
            m1_end = dt(d,8,0,0)
            m2_end = dt(d,8,0,40)
            int_times=[]
            for i,p in enumerate(prods):
                machine=1 if i%2==0 else 2
                prev=m1_end if machine==1 else m2_end
                pdef=PDICT[p]
                dsec=dur(pdef[1])
                setup=timedelta(seconds=random.randint(5,15))
                end_t = prev + dsec
                start_t = end_t - dsec
                if start_t.time() >= time(12,0) and start_t.time() < time(13,0):
                    start_t = dt(d,13,0,0)
                    end_t = start_t + dsec
                if end_t.time() > time(17,0):
                    end_t = dt(d,16,59,0)
                    start_t = end_t - dsec
                if machine==1: m1_end = end_t + setup
                else: m2_end = end_t + setup
                int_times.append((start_t,end_t))
            day_orders=[]
            for i,p in enumerate(prods):
                ono=f"ORD202601{order_no:05d}"
                order_no += 1
                int_worker = "TanakaJiro" if i < tanaka_target else "YamadaTaro"
                ext_worker = "KimuraNao" if i < ext_kimura else "SatoKen"
                pdef=PDICT[p]
                istart,iend=int_times[i]
                estart = iend + wait1(iend, plus=ext_wait_plus)
                edur = dur(pdef[2])
                if ext_worker=="KimuraNao" and d in KIMURA_BAD:
                    edur = timedelta(seconds=int(edur.total_seconds()*1.4))
                eend = estart + edur
                sstart = eend + wait2()
                sdur = dur(pdef[3])
                send = sstart + sdur
                if send.time() > time(17,0):
                    overflow = datetime.combine(d, time(17,0)) - send
                    sstart += overflow
                    send += overflow
                if sstart.time() < time(8,0):
                    sstart = dt(d,8,0,0); send = sstart + sdur
                if sstart.time() >= time(12,0) and sstart.time() < time(13,0):
                    sstart = dt(d,13,0,0); send = sstart + sdur
                ship_worker = "SuzukiMika"
                if d >= date(2026,1,27) and i >= 8:
                    ship_worker = "NakamuraRyo"
                ng=0
                if (order_no % 53)==0 or (order_no % 67)==0: ng=1
                day_orders.append(dict(date=d,order_no=ono,product=p,int_worker=int_worker,ext_worker=ext_worker,ship_worker=ship_worker,
                                       int_start=istart,int_end=iend,ext_start=estart,ext_end=eend,ship_start=sstart,ship_end=send,ng=ng,
                                       tehai_no=f"TH{order_no}",check_no=f"CHK{order_no}",slip_no=f"SLP{order_no}"))
            orders.extend(day_orders)
        validate(orders)
        low_days, kpi = kpi2(orders)
        int10_12, ext10_12 = kpi1_1012(orders)
        if low_days >=3:
            ext_wait_plus += 15
            continue
        if ext10_12 > int10_12:
            ext_wait_plus += 10
            continue
        break
    return orders

def validate(orders):
    for o in orders:
        assert o['int_end'] < o['ext_start'], f"{o['order_no']}: 内装end > 外装start"
        assert o['ext_end'] < o['ship_start'], f"{o['order_no']}: 外装end > 出荷検査start"
        assert o['int_end'].date() == o['int_start'].date(), f"{o['order_no']}: 内装が日またぎ"
        assert o['ext_end'].date() == o['ext_start'].date(), f"{o['order_no']}: 外装が日またぎ"
        assert o['ship_end'].date() == o['ship_start'].date(), f"{o['order_no']}: 出荷検査が日またぎ"
        assert time(8,0) <= o['int_start'].time() <= time(17,0)
        assert time(8,0) <= o['int_end'].time() <= time(17,0)
        assert time(8,0) <= o['ext_start'].time() <= time(17,0)
        assert time(8,0) <= o['ext_end'].time() <= time(17,0)
        assert time(8,0) <= o['ship_start'].time() <= time(17,0)
        assert time(8,0) <= o['ship_end'].time() <= time(17,0)

def kpi2(orders):
    low=0
    byday={}
    for d in DAYS:
        day=[o for o in orders if o['date']==d]
        peak=0; ptime='08:00'
        t=dt(d,8,0)
        while t<=dt(d,17,0):
            wip=sum(1 for o in day if o['int_end']<=t<o['ext_end'])
            if wip>peak: peak=wip; ptime=t.strftime('%H:%M')
            t += timedelta(minutes=15)
        byday[d]=(peak,ptime)
        if peak<4: low += 1
    return low, byday

def kpi1_1012(orders):
    i=sum(1 for o in orders if 10<=o['int_end'].hour<12)
    e=sum(1 for o in orders if 10<=o['ext_end'].hour<12)
    return i,e

def write_csvs(orders):
    base='results_record_db/sample_data'
    int_headers=['start_date','start_time','start_marker','end_date','end_time','end_marker','order_no']
    for worker in ['YamadaTaro','TanakaJiro']:
        with open(f'{base}/INTASM_{worker}_202601.csv','w',newline='',encoding='utf-8') as f:
            w=csv.writer(f); w.writerow(int_headers)
            for o in orders:
                if o['int_worker']==worker:
                    w.writerow([o['int_start'].strftime('%Y/%m/%d'),o['int_start'].strftime('%H:%M:%S'),'START',o['int_end'].strftime('%Y/%m/%d'),o['int_end'].strftime('%H:%M:%S'),'END',o['order_no']])
    ext_headers=['production_date_yymmdd','check_no','qr_read_ts','all_clear_ts','production_date','packing_date','tehai_no','order_no','product_name','width_mm','height_mm','material_code1','material_name1','material_qty1','material_code2','material_name2','material_qty2','qr_clear_count','initial_clear_count','forced_clear_count','material_pick_count','error_code']
    for worker in ['SatoKen','KimuraNao']:
        with open(f'{base}/EXTASM_{worker}_202601.csv','w',newline='',encoding='utf-8') as f:
            w=csv.writer(f); w.writerow(ext_headers)
            for o in orders:
                if o['ext_worker']==worker:
                    p=PDICT[o['product']]
                    w.writerow([o['date'].strftime('%y%m%d'),o['check_no'],o['ext_start'].strftime('%Y-%m-%d %H:%M:%S'),o['ext_end'].strftime('%Y-%m-%d %H:%M:%S'),o['date'].strftime('%Y-%m-%d'),o['date'].strftime('%Y-%m-%d'),o['tehai_no'],o['order_no'],o['product'],p[4],p[5],'M001','FRAME',1,'M002','SLAT',1,1,1,0,2,''])
    ship_headers=['inspector_name','inspection_date','slip_no','product_name','start_time','end_time','work_minutes','tehai_no','order_no','bottom_ng_count','slat_ng_count','balance_ng_count','ng_total']
    with open(f'{base}/SHIPCHK_202601.csv','w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(ship_headers)
        for o in orders:
            ng=o['ng']
            w.writerow([o['ship_worker'],o['date'].strftime('%Y-%m-%d'),o['slip_no'],o['product'],o['ship_start'].strftime('%H:%M:%S'),o['ship_end'].strftime('%H:%M:%S'),int((o['ship_end']-o['ship_start']).total_seconds()//60),o['tehai_no'],o['order_no'],ng,0,0,ng])
    with open(f'{base}/order_product_master.csv','w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['order_no','product_name'])
        for o in orders: w.writerow([o['order_no'],o['product']])

def print_summary(orders):
    print('=== 生成サマリ ===')
    print(f'総order_no件数: {len(orders)}件\n')
    print('[工程別レコード件数]')
    print(f'内装組立: {len(orders)}件')
    print(f'外装組立: {len(orders)}件')
    print(f'出荷検査: {len(orders)}件\n')

    def wk(d):
        return 1 if d.day<=9 else 2 if d.day<=16 else 3 if d.day<=23 else 4
    workers=['YamadaTaro','TanakaJiro','SatoKen','KimuraNao','SuzukiMika','NakamuraRyo']
    print('[作業者別・週別件数]')
    print('          第1週  第2週  第3週  第4週')
    for w in workers:
        c=[0,0,0,0]
        for o in orders:
            if o['int_worker']==w or o['ext_worker']==w or o['ship_worker']==w:
                c[wk(o['date'])-1]+=1
        print(f'{w:<11}{c[0]:>5}{c[1]:>6}{c[2]:>6}{c[3]:>6}')
    low, byday = kpi2(orders)
    print('\n[KPI2チェック: 内装完了済み・外装未完了の最大同時仕掛り件数（日別）]')
    for d in DAYS:
        p,t=byday[d]
        print(f'{d}: {p}件 (ピーク {t})')
    print('\n目標: 全日で最大仕掛り4件以上。4件未満の日が3日以上あれば要調整。')

    def band(ts):
        h=ts.hour
        if 8<=h<10: return 0
        if 10<=h<12: return 1
        if 13<=h<15: return 2
        if 15<=h<17: return 3
        return None
    c1=[0,0,0,0]; c2=[0,0,0,0]; c3=[0,0,0,0]
    for o in orders:
        b=band(o['int_end']);
        if b is not None: c1[b]+=1
        b=band(o['ext_end']);
        if b is not None: c2[b]+=1
        b=band(o['ship_end']);
        if b is not None: c3[b]+=1
    print('\n[KPI1チェック: 時間帯別完了件数（全期間合計）]')
    print(f'内装: 08-10時 {c1[0]}件 / 10-12時 {c1[1]}件 / 13-15時 {c1[2]}件 / 15-17時 {c1[3]}件')
    print(f'外装: 08-10時 {c2[0]}件 / 10-12時 {c2[1]}件 / 13-15時 {c2[2]}件 / 15-17時 {c2[3]}件')
    print(f'出荷: 08-10時 {c3[0]}件 / 10-12時 {c3[1]}件 / 13-15時 {c3[2]}件 / 15-17時 {c3[3]}件')

def main():
    orders=build()
    write_csvs(orders)
    print_summary(orders)

if __name__=='__main__':
    main()
