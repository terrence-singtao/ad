import re
from pathlib import Path
from datetime import datetime

ads_path = Path("/Volumes/ea524xr5/ext6/singtao/ad/ads.txt")
err_path = Path("/Users/tau/Downloads/Error-message.txt")

ads_lines = ads_path.read_text(encoding="utf-8").splitlines()
err_lines = err_path.read_text(encoding="utf-8").splitlines()

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup_path = ads_path.with_name(f"ads.txt.backup-before-fix-{timestamp}")
backup_path.write_text("\n".join(ads_lines) + "\n", encoding="utf-8")

line_errors = {}
current_line = None

for raw in err_lines:
    text = raw.strip()

    line_match = re.match(r"^Line\s+(\d+):$", text)
    if line_match:
        current_line = int(line_match.group(1))
        line_errors.setdefault(current_line, [])
        continue

    if current_line is not None and text.startswith("•"):
        message = text.lstrip("•").strip()
        line_errors[current_line].append(message)

delete_lines = set()
cert_fixes = {}

for line_no, messages in line_errors.items():
    for msg in messages:
        # Example:
        # Line is duplicated on line 2311.
        # Line is duplicated on lines 123 and 456.
        dup_match = re.search(r"Line is duplicated on line(?:s)?\s+(.+?)\.", msg)
        if dup_match:
            related_numbers = [line_no] + [
                int(n) for n in re.findall(r"\d+", dup_match.group(1))
            ]

            keep_line = min(related_numbers)

            for n in related_numbers:
                if n != keep_line:
                    delete_lines.add(n)

        # Example:
        # Certification authority ID is incorrect, correct ID for adyoulike.com is: 4ad745ead2958bf7
        #
        # Important:
        # TAG IDs here are treated as exactly 16 characters.
        # This avoids the earlier truncation problem such as:
        # f5ab79cb980f11d1 -> f5ab79cb9
        cert_match = re.search(
            r"Certification authority ID is incorrect,\s+correct ID for\s+[^ ]+\s+is:\s+([A-Za-z0-9]{16})\b",
            msg,
        )

        if cert_match:
            cert_fixes[line_no] = cert_match.group(1).lower()

def replace_or_add_cert_id(line, correct_id):
    # Preserve inline comments, e.g.
    # vdopia.com, 15364, RESELLER, 49a66ce31a704197 #video
    if "#" in line:
        main, comment = line.split("#", 1)
        comment = " #" + comment.strip()
    else:
        main, comment = line, ""

    parts = [p.strip() for p in main.rstrip().split(",")]

    # Only modify normal ads.txt records:
    # domain, publisher_id, DIRECT/RESELLER[, cert_id]
    if len(parts) < 3:
        return line

    if len(parts) >= 4:
        parts[3] = correct_id
        parts = parts[:4]
    else:
        parts.append(correct_id)

    return ", ".join(parts) + comment

new_lines = []
cert_fixed_count = 0

for original_line_no, line in enumerate(ads_lines, start=1):
    # Delete only higher-number duplicate lines.
    if original_line_no in delete_lines:
        continue

    # Fix cert ID only if this line is kept.
    if original_line_no in cert_fixes:
        line = replace_or_add_cert_id(line, cert_fixes[original_line_no])
        cert_fixed_count += 1

    new_lines.append(line)

ads_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

print("Done.")
print(f"Backup saved to: {backup_path}")
print(f"Duplicate lines removed: {len(delete_lines)}")
print(f"Certification authority ID fixes applied: {cert_fixed_count}")

if delete_lines:
    print("Removed duplicate line numbers:")
    print(", ".join(str(n) for n in sorted(delete_lines)))

if cert_fixes:
    print("Certification ID line numbers found:")
    print(", ".join(str(n) for n in sorted(cert_fixes)))