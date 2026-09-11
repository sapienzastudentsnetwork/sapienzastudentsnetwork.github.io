#!/usr/bin/env python3
"""Download published CSV timetables and use them only to correct classroom data."""

import csv, io, json, os, re, shutil, tempfile, unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vRXJvRaxRlv_h_ukp2ww0kWAUmZb-DADQa-QPGucIgsiJecf91Gs_2fmijhuERPAoL-wbuIjsNO3oYo/"
    "pub?output=csv&single=true&gid={gid}"
)
SHEETS = {
    "33502_ACSAI.csv": "511536458",
    "33503_Informatica.csv": "1890069020",
    "33508_Computer-Science.csv": "259872005",
    "33516_Cybersecurity.csv": "1324510703",
    "33519_Data-Science.csv": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPHqCaCRU-5HE9gpoFs3f2Ru6YeIF8NVuzwlg1cwN7SjTmGvsG6r5esVgqCC7x5gEHl7BxLNLxUncI/pubhtml?gid=1780311734&single=true",
}
HEADERS = {"timetable", "orario"}
TIME_RE = re.compile(r"^\s*(\d{1,2})[:.]\d{2}\s*[-–—]\s*\d{1,2}[:.]\d{2}\s*$")
CODE_RE = re.compile(r"\b(AAF\d+|\d{5,8})(?:\s*/\s*(AAF\d+|\d{5,8}))?\b", re.I)
BUILDING_RE = re.compile(r"\b((?:RM|CU)\d{3})\b", re.I)
YEAR_RE = re.compile(
    r"(?i)(?:\b([123])(?:st|nd|rd|th)\s+year\b|\b([iv]{1,3})\s+anno\b)"
)
DAY_MAP = {
    "monday": "lunedì",
    "lunedi": "lunedì",
    "lunedì": "lunedì",
    "tuesday": "martedì",
    "martedi": "martedì",
    "martedì": "martedì",
    "wednesday": "mercoledì",
    "mercoledi": "mercoledì",
    "mercoledì": "mercoledì",
    "thursday": "giovedì",
    "giovedi": "giovedì",
    "giovedì": "giovedì",
    "friday": "venerdì",
    "venerdi": "venerdì",
    "venerdì": "venerdì",
}
ROMAN = {"i": "1", "ii": "2", "iii": "3"}


def norm(s):
    return " ".join(str(s).replace("\ufeff", "").split()).strip()


def key(s):
    s = (
        unicodedata.normalize("NFKD", norm(s))
        .encode("ascii", "ignore")
        .decode()
        .casefold()
    )
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def is_header(r):
    return bool(r) and key(r[0]) in HEADERS


def is_time(r):
    return bool(r) and bool(TIME_RE.match(norm(r[0])))


def read_rows(data):
    return list(csv.reader(io.StringIO(data.decode("utf-8-sig"), newline="")))


def label_before(rows, start, header):
    for r in reversed(rows[start:header]):
        if r and norm(r[0]) and not is_header(r) and not is_time(r):
            return norm(r[0])
    return ""


def suffix(label, n):
    normalized = norm(label)
    m = YEAR_RE.search(normalized) or re.search(
        r"(?i)\byear[_ -]?([123])\b", normalized
    )
    parts = []
    if m:
        raw = m.group(1) or (m.group(2) if m.lastindex and m.lastindex >= 2 else None)
        year = ROMAN.get(raw.casefold(), raw)
        parts.append({"1": "1st-year", "2": "2nd-year", "3": "3rd-year"}[year])
    c = re.search(r"(?i)\b([AM])(?:-|_|\s)+(?:channel(?:-|_|\s)+)?([LZ])\b", normalized)
    if c:
        parts.append(f"{c.group(1).upper()}-{c.group(2).upper()}")
    if not parts and re.search(r"(?i)single[_ -]+channel|canale\s+unico", normalized):
        return ""
    if not parts and label:
        v = re.sub(r"(?i)^.*?\)\s*-?\s*", "", norm(label)).strip(" -")
        parts.append(re.sub(r"[^A-Za-z0-9]+", "-", v).strip("-") or str(n))
    return "_".join(parts) if parts else str(n)


def split_sections(rows):
    hs = [i for i, r in enumerate(rows) if is_header(r)]
    out = []
    prev = 0
    if not hs:
        raise ValueError("No timetable header found")
    for n, h in enumerate(hs, 1):
        end = hs[n] if n < len(hs) else len(rows)
        block = rows[h:end]
        last = max((i for i, r in enumerate(block) if is_time(r)), default=None)
        if last is None:
            continue
        out.append((suffix(label_before(rows, prev, h), n), block[: last + 1]))
        prev = h + last + 1
    return out


def write_raw(source_name, rows, raw_dir):
    generated = []
    for n, (section, block) in enumerate(split_sections(rows), 1):
        stem = Path(source_name).stem
        # Keep degree code and readable programme/curriculum; omit single-channel noise.
        name = stem + ("_" + section if section else "") + ".csv"
        path = raw_dir / name
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f, lineterminator="\n").writerows(block)
        generated.append((path, block))
    return generated


def parse_room(cell):
    # Parse classroom names only after Aula/Aule, so hyphens in technical IDs such as
    # RM102-E01PR1L007 are never interpreted as classroom separators.
    buildings = [value.upper() for value in BUILDING_RE.findall(norm(cell))]
    rooms = []
    pattern = re.compile(
        r"(?i)\bAul[ae]\s+((?:Informatica\s+)?[A-Z]*\d+[A-Z]*|[A-Z]+)"
        r"(?:\s*(?:-|/)\s*([A-Z]*\d+[A-Z]*))?"
    )
    for match in pattern.finditer(cell):
        first = norm(match.group(1))
        second = norm(match.group(2) or "")
        rooms.append(f"Aula {first}")
        if second:
            # Aula A5-6 means Aula A5 + Aula A6; Aula 15-17 remains numeric.
            prefix_match = re.match(r"([A-Za-z]+)", first)
            if prefix_match and second[0].isdigit():
                second = prefix_match.group(1) + second
            rooms.append(f"Aula {second}")
    if len(buildings) == 1:
        # A shared location/building following a range applies to every expanded room.
        return [(room, buildings[0]) for room in rooms]
    return [
        (room, buildings[i] if i < len(buildings) else None)
        for i, room in enumerate(rooms)
    ]


def csv_entries(source_name, block):
    degree = source_name.split("_", 1)[0]
    section = Path(source_name).stem
    channel = "0"
    if section.endswith("_A-L"):
        channel = "1"
    elif section.endswith("_M-Z"):
        channel = "2"
    header = block[0]
    entries = []
    for row in block[1:]:
        tm = TIME_RE.match(norm(row[0]) if row else "")
        if not tm:
            continue
        start = str(int(tm.group(1)))
        for col, cell in enumerate(row[1:], 1):
            if not norm(cell) or col >= len(header):
                continue
            day = DAY_MAP.get(key(header[col]))
            cm = CODE_RE.search(cell)
            if not day or not cm:
                continue
            codes = [c for c in cm.groups() if c]
            unit = None
            um = re.search(
                r"(?i)\bUNIT\s*(I{1,3}|\d+)\b|\b(I{1,3}|\d+)\s+MODULO\b", cell
            )
            if um:
                u = next(x for x in um.groups() if x)
                unit = ROMAN.get(u.casefold(), u)
            candidates = []
            for c in codes:
                candidates.extend(([f"{c}_{unit}", c] if unit else [c]))
            entries.append(
                {
                    "degree": degree,
                    "channel": channel,
                    "day": day,
                    "start": start,
                    "codes": candidates,
                    "rooms": parse_room(cell),
                    "cell": norm(cell),
                }
            )
    return entries


def room_key(value):
    s = key(value)
    s = re.sub(r"^aula informatica ", "informatica ", s)
    s = re.sub(r"^aula ", "", s)
    s = re.split(r"\b(?:via|viale|edificio|citta|de lollis)\b", s, 1)[0].strip()
    s = re.sub(r"^(\d+)l$", r"\1", s)
    return s


def display_score(value):
    # Prefer the richest existing timetable label for a classroom ID.
    # Example: "Aula C - Città Universitaria (CU035-E01PTEL011)" beats "Aula C".
    return (
        bool(re.search(r"\b(?:RM|CU)\d{3}(?:-[A-Z0-9]+)?\b", value, re.I)),
        len(value),
    )


def classroom_index(timetables, classrooms):
    idx = {}
    names = {}
    canonical = {}
    for course in timetables.values():
        for days in course.get("channels", {}).values():
            for schedules in days.values():
                for schedule in schedules:
                    for cid, display in schedule.get("classrooms", {}).items():
                        previous = canonical.get(cid)
                        if previous is None or display_score(display) > display_score(
                            previous
                        ):
                            canonical[cid] = display
    for cid, meta in classrooms.items():
        description = meta.get("description", "")
        if description and cid not in canonical:
            canonical[cid] = description
    for cid, display in canonical.items():
        b = BUILDING_RE.search(display)
        room = re.sub(r"\s*\(Edificio:.*$", "", display, flags=re.I)
        room = re.sub(r"\s*-\s*(?:Citt[aà].*|Via .*|Viale .*)$", "", room, flags=re.I)
        idx[(room_key(room), b.group(1).upper() if b else None)] = cid
        names.setdefault(room_key(room), set()).add(cid)
    for cid, meta in classrooms.items():
        room = re.sub(r"\s*-\s*.*$", "", meta.get("description", "")).strip()
        if room:
            names.setdefault(room_key(room), set()).add(cid)
    return idx, names, canonical


def resolve_room(room, building, idx, names, canonical):
    cid = idx.get((room_key(room), building))
    if cid:
        return cid, canonical[cid]
    choices = names.get(room_key(room), set())
    if len(choices) == 1:
        cid = next(iter(choices))
        return cid, canonical[cid]
    return None


def debug_unresolved(reason, e, extra=""):
    details = (
        f"degree={e['degree']} channel={e['channel']} day={e['day']} "
        f"start={e['start']} codes={','.join(e['codes'])}"
    )
    suffix = f" {extra}" if extra else ""
    print(f"[CSV DEBUG] {reason}: {details}{suffix}")


def merge(entries, timetables, classrooms):
    idx, names, canonical = classroom_index(timetables, classrooms)
    stats = {
        "matched": 0,
        "changed": 0,
        "unresolved": 0,
        "ambiguous": 0,
        "course_not_found": 0,
        "slot_not_found": 0,
    }
    for e in entries:
        course = None
        matched_code = None
        for code in e["codes"]:
            candidate = timetables.get(code)
            if candidate and e["degree"] in candidate.get(
                "degrees", [candidate.get("degree")]
            ):
                course = candidate
                matched_code = code
                break
        if not course:
            stats["course_not_found"] += 1
            debug_unresolved("COURSE_NOT_FOUND", e)
            continue
        schedules = course.get("channels", {}).get(e["channel"], {}).get(e["day"], [])
        same = [
            schedule
            for schedule in schedules
            if str(schedule.get("timeslot", "")).split("-", 1)[0].strip() == e["start"]
        ]
        if not same:
            stats["slot_not_found"] += 1
            available = (
                ",".join(str(x.get("timeslot", "")) for x in schedules) or "none"
            )
            debug_unresolved(
                "SLOT_NOT_FOUND",
                e,
                f"matched_code={matched_code} available={available}",
            )
            continue
        if len(same) > 1:
            stats["ambiguous"] += 1
            debug_unresolved(
                "SLOT_AMBIGUOUS", e, f"matched_code={matched_code} count={len(same)}"
            )
            continue
        if not e["rooms"]:
            stats["unresolved"] += 1
            debug_unresolved(
                "NO_ROOM_PARSED", e, f"matched_code={matched_code} cell={e['cell']!r}"
            )
            continue
        resolved = {}
        missing = []
        for room, building in e["rooms"]:
            result = resolve_room(room, building, idx, names, canonical)
            if result:
                resolved[result[0]] = result[1]
            else:
                missing.append(f"{room} [{building or 'no-building'}]")
        if not resolved:
            stats["unresolved"] += 1
            debug_unresolved(
                "CLASSROOM_NOT_FOUND",
                e,
                f"matched_code={matched_code} csv_rooms={'; '.join(missing)}",
            )
            continue
        if missing:
            debug_unresolved(
                "CLASSROOM_PARTIALLY_RESOLVED",
                e,
                f"matched_code={matched_code} missing={'; '.join(missing)}",
            )
        stats["matched"] += 1
        schedule = same[0]
        if (
            schedule.get("classrooms") != resolved
            or "classroomInfo" in schedule
            or "classroomUrl" in schedule
        ):
            schedule["classrooms"] = resolved
            schedule.pop("classroomInfo", None)
            schedule.pop("classroomUrl", None)
            stats["changed"] += 1
            print(
                f"[CSV UPDATE] degree={e['degree']} code={matched_code} channel={e['channel']} day={e['day']} start={e['start']} classrooms={resolved}"
            )
    return stats


def obtain(name, gid, fixture_dir=None, timeout=10):
    if fixture_dir:
        # Fixture names are the old exporter names; find by degree/programme prefix.
        prefix = Path(name).stem.split("_", 1)[1].replace("-", "_")
        candidates = list(Path(fixture_dir).glob(prefix + ".csv"))
        if candidates:
            return candidates[0].read_bytes()

    url = (
        gid.replace("/pubhtml?", "/pub?output=csv&")
        if gid.startswith("http")
        else BASE_URL.format(gid=gid)
    )
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urlopen(request, timeout=timeout) as response:
        data = response.read()
    if not data:
        raise ValueError(f"Empty CSV response for {name}")
    return data


def raw_files_for_source(raw_directory, source_name):
    source_stem = Path(source_name).stem
    return sorted(raw_directory.glob(f"{source_stem}_*.csv"))


def entries_from_raw_snapshot(raw_directory, source_name):
    raw_files = raw_files_for_source(raw_directory, source_name)
    if not raw_files:
        raise RuntimeError(
            f"The download of {source_name} failed and no previous raw CSV "
            "snapshot exists for that spreadsheet"
        )

    entries = []
    for path in raw_files:
        rows = read_rows(path.read_bytes())
        if not rows or not is_header(rows[0]):
            raise ValueError(f"Invalid raw CSV snapshot: {path.name}")
        entries.extend(csv_entries(path.name, rows))

    print(
        f"[CSV DOWNLOAD] Using the existing raw snapshot for {source_name} "
        f"({len(raw_files)} files)."
    )
    return entries


def replace_raw_files(raw_directory, source_name, rows):
    with tempfile.TemporaryDirectory() as temporary_directory:
        temporary_path = Path(temporary_directory)
        generated = write_raw(source_name, rows, temporary_path)

        # The new files have already been generated successfully. Replace only
        # the raw files belonging to this spreadsheet, leaving all others alone.
        for path in raw_files_for_source(raw_directory, source_name):
            path.unlink()

        entries = []
        for temporary_file, block in generated:
            destination = raw_directory / temporary_file.name
            shutil.move(str(temporary_file), destination)
            entries.extend(csv_entries(destination.name, block))
        return entries


def main():
    root = Path(__file__).resolve().parents[1]
    data = root / "data"
    raw = root / "static" / "timetables_csv_raw"
    raw.mkdir(parents=True, exist_ok=True)
    fixture = os.getenv("CSV_TIMETABLES_FIXTURE_DIR")
    entries = []

    for name, gid in SHEETS.items():
        try:
            rows = read_rows(obtain(name, gid, fixture))
            # Validate and split this spreadsheet before replacing its previous
            # raw files. A failure affects only this specific spreadsheet.
            entries.extend(replace_raw_files(raw, name, rows))
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
            print(f"[CSV DOWNLOAD] Could not refresh {name}: {error}.")
            entries.extend(entries_from_raw_snapshot(raw, name))

    timetables = json.loads((data / "timetables.json").read_text())
    classrooms = json.loads((data / "classrooms.json").read_text())
    stats = merge(entries, timetables, classrooms)
    (data / "timetables.json").write_text(
        json.dumps(timetables, ensure_ascii=True, indent=2) + "\n"
    )
    print(json.dumps({"csv_entries": len(entries), **stats}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
