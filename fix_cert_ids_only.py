import re
from pathlib import Path
from datetime import datetime

ads_path = Path("/Volumes/ea524xr5/ext6/singtao/ad/ads.txt")

known_tag_ids = {
    "google.com": "f08c47fec0942fa0",
    "appnexus.com": "f5ab79cb980f11d1",
    "xandr.com": "f5ab79cb980f11d1",
    "rubiconproject.com": "0bfd66d529a55807",
    "pubmatic.com": "5d62403b186f2ace",
    "openx.com": "6a698e2ec38604c6",
    "indexexchange.com": "50b1c356f2c5c8fc",
    "contextweb.com": "89ff185a4c4e857c",
    "lijit.com": "fafdf38b16bf6b2b",
    "sovrn.com": "fafdf38b16bf6b2b",
    "smartadserver.com": "060d053dcf45cbf3",
    "themediagrid.com": "35d5010d7789b49d",
    "sharethrough.com": "d53b998a7bd4ecd2",
    "triplelift.com": "6c33edb13117fd86",
    "criteo.com": "9fac4a4a87c2a44f",
    "conversantmedia.com": "03113cd04947736d",
    "smaato.com": "07bcf65f187117b4",
    "loopme.com": "6c8d5f95897a5a3b",
    "inmobi.com": "83e75a7ae333ca9d",
    "sonobi.com": "d1a215d9eb5aee9e",
    "rhythmone.com": "a670c89d4a324e47",
    "video.unrulymedia.com": "6f752381ad5ec0e5",
    "33across.com": "bbea06d9c4d2853c",
    "e-planning.net": "c1ba615865ed87b2",
    "adform.com": "9f5210a2f0999e32",
    "teads.tv": "15a9c44f6d26cbe1",
    "emxdgt.com": "1e1d41537f7cad7f",
    "ssp.cadent.com": "1e1d41537f7cad7f",
    "springserve.com": "a24eb641fc82e93d",
    "primis.tech": "b6b21d256ef43532",
    "incrementx.com": "8728b7e97e589da4",
    "gumgum.com": "ffdef49475d318a9",
    "trustx.org": "1d2c8a747a749d25",
    "yahoo.com": "e1a5b5b6e3255540",
    "tremorhub.com": "1a4e959a1b50034a",
    "telaria.com": "1a4e959a1b50034a",
    "chocolateplatform.com": "49a66ce31a704197",
    "vdopia.com": "49a66ce31a704197",
    "districtm.io": "3fd707be9c4527c3",
    "pubnative.net": "d641df8625486a7b",
    "beachfront.com": "e2541279e8e2ca4d",
    "pokkt.com": "c45702d9311e25fd",
    "xad.com": "81cbf0a75a5e0e9a",
    "verve.com": "0c8f5958fc2d6270",
    "mgid.com": "d4c29acad76ce94f",
    "mobilefuse.com": "71e88b065d69c021",
    "opera.com": "55a0c5fd61378de3",
    "videoheroes.tv": "064bc410192443d8",
    "spotxchange.com": "7842df1d2fe2db34",
    "spotx.tv": "7842df1d2fe2db34",
}

lines = ads_path.read_text(encoding="utf-8").splitlines()

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup_path = ads_path.with_name(f"ads.txt.repair-cert-backup-{timestamp}")
backup_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

fixed = 0
new_lines = []

for line in lines:
    stripped = line.strip()

    if not stripped or stripped.startswith("#") or "=" in stripped:
        new_lines.append(line)
        continue

    if "#" in line:
        main, comment = line.split("#", 1)
        comment = " #" + comment.strip()
    else:
        main, comment = line, ""

    parts = [p.strip() for p in main.rstrip().split(",")]

    if len(parts) < 3:
        new_lines.append(line)
        continue

    domain = parts[0].lower()

    if domain in known_tag_ids:
        correct_id = known_tag_ids[domain]

        if len(parts) >= 4:
            if parts[3] != correct_id:
                parts[3] = correct_id
                fixed += 1
        else:
            parts.append(correct_id)
            fixed += 1

        line = ", ".join(parts[:4]) + comment

    new_lines.append(line)

ads_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

print("Done.")
print(f"Backup saved to: {backup_path}")
print(f"Certification IDs repaired/added: {fixed}")