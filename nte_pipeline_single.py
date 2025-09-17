# nte_pipeline_single.py
# Girdi:  dersler.json, departments.json ve {nte_yeni2.json | ntetum.json | nte.json} (en az biri)
# Çıktı:  nte_time_with_codes.json (tek dosya)
#
# Çalıştırma:
#   python nte_pipeline_single.py

import json
from pathlib import Path
from datetime import datetime

P_DERSLER      = Path("data.json")
P_DEPARTMENTS  = Path("departments.json")
NTE_CANDIDATES = [Path("nte-list.json"), Path("ntetum.json"), Path("nte.json")]
OUT            = Path("nte-available.json")

DAY = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def dump_json(path: Path, data) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_nte_any():
    for p in NTE_CANDIDATES:
        if p.exists():
            log(f"NTE kaynağı: {p.name}")
            return load_json(p)
    raise FileNotFoundError("NTE listesi bulunamadı (nte_yeni2.json / ntetum.json / nte.json).")

def deptify(prefix: str, full_code: str) -> str:
    # prefix_merger.py ile aynı: 4. hane '0' ise atla, değilse dahil et
    return prefix + (full_code[4:] if len(full_code) >= 4 and full_code[3] == "0" else full_code[3:])

def get_prefixed_code(numeric_code: str, dept_map: dict) -> str | None:
    dept_id = numeric_code[:3]
    prefix = (dept_map.get(dept_id) or {}).get("p")
    if not prefix or prefix == "-no course-":
        return None
    return deptify(prefix, numeric_code)

def is_available_section(sec: dict) -> bool:
    """Kısıt yoksa ya da d == 'ALL' varsa şube uygun kabul edilir."""
    cons = sec.get("c", [])
    return (not cons) or any(item.get("d") == "ALL" for item in cons)

def build_available_index(dersler: dict, dept_map: dict) -> dict:
    """
    Prefiks indeksini SADECE 'available' şubesi olan derslerden kurar.
    Dönüş: "ARCH440" -> {"numeric": "1200440", "name": "ARCH440 - ..."}
    """
    idx = {}
    for numeric_id, course in dersler.items():
        sections = course.get("Sections", {}) or {}
        if not any(is_available_section(s) for s in sections.values()):
            continue  # hiç uygun şubesi yoksa bu dersi alma

        pref = get_prefixed_code(str(numeric_id), dept_map)
        if not pref:
            continue

        name = course.get("Course Name", "") or ""
        display = name
        head = display.split(" - ", 1)[0]
        # Başta prefiksli ifade yoksa görünür ada prefiksi ekleyelim
        if head.isdigit() or head == display:
            display = f"{pref} - {name.split(' - ', 1)[-1]}" if " - " in name else f"{pref} - {name}"

        idx[pref] = {"numeric": str(numeric_id), "name": display}
    return idx

def build_course_output(numeric_id: str, pref_code: str, display_name: str, credits: str, dersler: dict) -> dict:
    """
    Bir dersi (numeric_id) alır; SADECE 'available' şubelerini, zamanlarını ve eğitmenlerini ekler.
    """
    course = dersler.get(numeric_id, {}) or {}
    sections = course.get("Sections", {}) or {}

    out_sections = []
    for sid, sec in sections.items():
        if not is_available_section(sec):
            continue

        # Zamanlar
        times = sec.get("t", []) or []
        if not times:
            time_list = [{"day": "No Timestamp Added Yet"}]
        else:
            time_list = []
            for t in times:
                d = t.get("d")
                day = DAY.get(d, "no day info") if isinstance(d, int) else "no day info"
                time_list.append({
                    "day": day,
                    "start": t.get("s", ""),
                    "end":   t.get("e", ""),
                    "room":  t.get("p", "")
                })

        # Eğitmenler
        instructors = sec.get("i", []) or []

        out_sections.append({
            "section_id": sid,
            "times": time_list,
            "instructors": instructors
        })

    if not out_sections:
        out_sections = [{
            "section_id": "not found",
            "times": [{"day": "No Timestamp Added Yet"}],
            "instructors": []
        }]

    return {
        "code": {"departmental": pref_code, "numeric": numeric_id, "matched_by": "prefixed"},
        "name": display_name,
        "credits": credits,
        "sections": out_sections
    }

def main():
    if not P_DERSLER.exists():
        raise FileNotFoundError("dersler.json yok.")
    if not P_DEPARTMENTS.exists():
        raise FileNotFoundError("departments.json yok.")

    dersler = load_json(P_DERSLER)
    dept_map = load_json(P_DEPARTMENTS)
    nte = load_nte_any()

    # Prefiks indeks (sadece available derslerden)
    index = build_available_index(dersler, dept_map)

    matched = 0
    missed = 0
    out = []

    # NTE listesi dict veya liste olabilir
    iterable = (c for lst in nte.values() for c in lst) if isinstance(nte, dict) else iter(nte)

    for c in iterable:
        raw = (c.get("code") or c.get("Code") or "").strip()
        credits = c.get("credits") or c.get("Credits") or ""
        key = raw.replace(" ", "")  # "ARCH 440" -> "ARCH440"

        hit = index.get(key)
        if not hit:
            missed += 1
            continue

        out.append(build_course_output(hit["numeric"], key, hit["name"], credits, dersler))
        matched += 1

    dump_json(OUT, out)
    log(f"[DONE] matched: {matched}, missed: {missed} -> {OUT.name}")

if __name__ == "__main__":
    main()
