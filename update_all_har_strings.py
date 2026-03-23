#!/usr/bin/env python3
import sys, re, json, math, glob, os, datetime

# JS Math Replicas
R = math.pi / 180; D = 180 / math.pi
SIN = lambda a: math.sin(a * R); COS = lambda a: math.cos(a * R); TAN = lambda a: math.tan(a * R)
ASIN = lambda x: math.asin(x) * D; ACOS = lambda x: math.acos(max(-1.0, min(1.0, x))) * D
ACOT = lambda x: math.atan(1.0 / x) * D
fxa  = lambda a: a - 360 * math.floor(a / 360)

def jd(y, m, d):
    if m <= 2: y -= 1; m += 12
    A = math.floor(y / 100); B = 2 - A + math.floor(A / 4)
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + B - 1524.5

def sun_pos(j):
    T = (j - 2451545) / 36525
    L0 = fxa(280.46646 + 36000.76983 * T + 0.0003032 * T * T)
    M = fxa(357.52911 + 35999.05029 * T - 0.0001537 * T * T)
    e = 0.016708634 - 0.000042037 * T - 0.0000001267 * T * T
    C = ((1.914602 - 0.004817 * T - 0.000014 * T * T) * SIN(M)
         + (0.019993 - 0.000101 * T) * SIN(2 * M) + 0.000289 * SIN(3 * M))
    om = fxa(125.04 - 1934.136 * T); lam = L0 + C - 0.00569 - 0.00478 * SIN(om)
    eps = (23 + (26 + (21.448 - 46.815*T - 0.00059*T*T + 0.001813*T*T*T) / 60) / 60 + 0.00256 * COS(om))
    decl = ASIN(SIN(eps) * SIN(lam))
    y2 = TAN(eps / 2) ** 2
    eqt = (y2 * SIN(2 * L0) - 2 * e * SIN(M) + 4 * e * y2 * SIN(M) * COS(2 * L0)
           - 0.5 * y2 * y2 * SIN(4 * L0) - 1.25 * e * e * SIN(2 * M))
    return {'decl': decl, 'eqt': eqt * D * 4 / 60}

def ha(a, lat, decl):
    n = -SIN(a) - SIN(lat) * SIN(decl); dn = COS(lat) * COS(decl); r = n / dn
    if r > 1 or r < -1: return 0
    return ACOS(r) / 15

def compute_base_times(y, m, d, lat, lng, alt, tz=3):
    j = jd(y, m, d); s = sun_pos(j)
    t = 12 + tz - (lng / 15.0) - s['eqt']
    dip = 0.0347 * math.sqrt(max(0, alt)); sr = (50 / 60.0) + dip
    hf = ha(18.0, lat, s['decl']); hss = ha(sr, lat, s['decl']); hi = ha(17.0, lat, s['decl'])
    an = (SIN(ACOT(1 + TAN(abs(s['decl'] - lat)))) - SIN(lat) * SIN(s['decl']))
    hasr = ACOS(an / (COS(lat) * COS(s['decl']))) / 15.0
    return [t - hf, t - hss, t, t + hasr, t + hss, t + hi]

def compute_delta(base_h, diyanet_hhmm):
    diyanet_m = int(diyanet_hhmm.split(':')[1])
    diyanet_hh = int(diyanet_hhmm.split(':')[0])
    for delta in range(-30, 31):
        corrected_h = base_h + delta / 60.0
        frac = (corrected_h - math.floor(corrected_h)) * 60
        js_rounded_mins = math.floor(frac - 0.035 + 0.5)
        if js_rounded_mins % 60 == diyanet_m:
            corrected_hh = int(math.floor(corrected_h))
            if js_rounded_mins == 60: corrected_hh += 1
            elif js_rounded_mins < 0:
                js_rounded_mins = 59
                corrected_hh -= 1
            if corrected_hh % 24 == diyanet_hh % 24:
                return delta
    return 0

def normalize_tr(text):
    tr_map = {'ç':'c', 'ğ':'g', 'ı':'i', 'i':'i', 'ö':'o', 'ş':'s', 'ü':'u',
              'Ç':'C', 'Ğ':'G', 'İ':'I', 'I':'I', 'Ö':'O', 'Ş':'S', 'Ü':'U',
              'â':'a', 'Â':'A', 'î':'i', 'Î':'I'}
    for k, v in tr_map.items(): text = text.replace(k, v)
    return text.upper()

def process():
    file_path = '/Users/zencefilefendi/Desktop/namaz/Diyanet_Offline_Motor.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    match = re.search(r'(const\s+IL_ILCE_DB\s*=\s*)(\{.*?\});', html, re.DOTALL)
    if not match:
        print("IL_ILCE_DB not found!")
        return
        
    prefix = match.group(1)
    db_str = match.group(2)
    db = json.loads(db_str)
    
    aylar = {"Ocak":1,"Şubat":2,"Mart":3,"Nisan":4,"Mayıs":5,"Haziran":6,"Temmuz":7,"Ağustos":8,"Eylül":9,"Ekim":10,"Kasım":11,"Aralık":12}
    
    repo_path = "/tmp/namaz_vakitleri_repo"
    success = 0
    failed = 0
    total_ilce = sum(len(cities) for cities in db.values())
    
    for il, ilceler in db.items():
        if il == "Amerika Birleşik Devletleri": continue
        for ilce, data in ilceler.items():
            if 'lat' not in data or 'lng' not in data: continue
            
            norm_ilce = normalize_tr(ilce)
            if norm_ilce == "MERKEZ":
                norm_ilce = normalize_tr(il)
                
            # Find json file
            search_pattern = os.path.join(repo_path, f"{norm_ilce}_*.json")
            files = glob.glob(search_pattern)
            
            # Special cases
            if not files:
                norm_il = normalize_tr(il)
                search_pattern2 = os.path.join(repo_path, f"{norm_ilce}_{norm_il}_*.json")
                files = glob.glob(search_pattern2)
            
            if not files:
                search_pattern3 = os.path.join(repo_path, f"{norm_il}_*.json")
                files = glob.glob(search_pattern3)
                
            if not files:
                print(f"File not found for {il} - {ilce} ({norm_ilce})")
                failed += 1
                continue
                
            with open(files[0], 'r', encoding='utf-8') as f:
                diyanet_arr = json.load(f)
                
            if len(diyanet_arr) < 365:
                print(f"Skipping {ilce}, less than 365 days")
                continue
                
            har_chars = []
            for row in diyanet_arr:
                parts = row['miladiTarih'].split()
                if len(parts) >= 3:
                    d = int(parts[0])
                    m = aylar[parts[1]]
                    y = int(parts[2])
                    
                    diyanet = [row['imsak'], row['gunes'], row['ogle'], row['ikindi'], row['aksam'], row['yatsi']]
                    bases = compute_base_times(y, m, d, data['lat'], data['lng'], data['alt'])
                    
                    for i, base in enumerate(bases):
                        delta = compute_delta(base, diyanet[i])
                        char_val = 77 + delta
                        char_val = max(65, min(90, char_val))
                        har_chars.append(chr(char_val))
            
            data['har'] = "".join(har_chars)
            success += 1
            if success % 50 == 0:
                print(f"Processed {success}/{total_ilce} districts...")

    new_db_str = json.dumps(db, ensure_ascii=False)
    new_html = html[:match.start(2)] + new_db_str + html[match.end(2):]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
        
    print(f"Done! Successfully recalibrated {success} districts. Failed: {failed}")

if __name__ == '__main__':
    process()
