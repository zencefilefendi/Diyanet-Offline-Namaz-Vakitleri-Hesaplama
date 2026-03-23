import json, re, zlib, struct

html_path = '/Users/zencefilefendi/Desktop/namaz/Diyanet_Offline_Motor.html'
out_h_path = '/Users/zencefilefendi/Desktop/namaz/arduino_engine/diyanet_db.h'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const IL_ILCE_DB = (\{.*?\});', text, re.DOTALL)
db = json.loads(m.group(1))

print("Generating C++ PROGMEM Headers for Arduino Engine...")

raw_payload = ""
districts_struct = []
district_count = 0
har_global_offset = 0

for il, ilceler in db.items():
    for ilce, data in ilceler.items():
        if 'har' in data:
            lat = data['lat']
            lng = data['lng']
            alt = data['alt']
            har = data['har']
            
            # C struct: {lat, lng, alt, har_idx}
            districts_struct.append((il, ilce, lat, lng, alt, har_global_offset))
            
            raw_payload += har
            har_global_offset += 2190
            district_count += 1

compressed = zlib.compress(raw_payload.encode('ascii'), level=9)

with open(out_h_path, 'w', encoding='utf-8') as f:
    f.write("// Diyanet Offline Motor V3 - Ultra Compressed Arduino Engine\n")
    f.write("// DO NOT MODIFY: Auto-generated via Harmonic Delta Signature ZLIB compression\n\n")
    f.write("#include <Arduino.h>\n\n")
    f.write(f"const uint32_t TOTAL_DISTRICTS = {district_count};\n")
    f.write(f"const uint32_t ZLIB_PAYLOAD_SIZE = {len(compressed)};\n\n")
    
    f.write("typedef struct {\n")
    f.write("  float lat;\n  float lng;\n  int16_t alt;\n  uint32_t har_offset;\n")
    f.write("} DistrictMetadata;\n\n")
    
    f.write("const DistrictMetadata PROGMEM diyanet_districts[] = {\n")
    for i, (_, _, lat, lng, alt, offset) in enumerate(districts_struct):
        f.write(f"  {{ {lat:.4f}, {lng:.4f}, {alt}, {offset} }}")
        if i < len(districts_struct) - 1:
            f.write(",\n")
        else:
            f.write("\n")
    f.write("};\n\n")
    
    f.write("// ZLIB DEFLATE Byte Array for all HAR strings (Stream Decompress lazily on boot)\n")
    f.write("const uint8_t PROGMEM diyanet_har_zlib[] = {\n  ")
    for i, b in enumerate(compressed):
        f.write(f"0x{b:02X}, ")
        if (i + 1) % 16 == 0:
            f.write("\n  ")
    f.write("\n};\n")

print(f"Header generated at {out_h_path}")
print(f"Final ZLIB Flash Memory footprint: {len(compressed)/1024:.2f} KB!")
