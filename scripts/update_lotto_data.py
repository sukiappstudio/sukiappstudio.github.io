#!/usr/bin/env python3
"""Refreshes the static mirror of the official lottery data that the 로또도사 Toss mini-app reads.

Run from the root of the sukiappstudio.github.io repository:

  python3 scripts/update_lotto_data.py            # updates data/lotto-sage/
  python3 scripts/update_lotto_data.py --strict   # exit 1 when the official site could not be read

Files (data/lotto-sage/):
  lotto645.csv       full Lotto 6/45 history, the app's bundled CSV format (DrawData.CSV_HEADER)
  pension720.csv     full 연금복권720+ history with winner counts (PensionData.CSV_HEADER)
  stores-recent.csv  winner stores of the latest 52 Lotto and 52 pension draws, one block per draw:
                     "# lotto round=N online1=a online2=b" (or "# pension round=N ...") followed by
                     StoreData.roundToCsv's header "round,rank,method,id,name,address,region,lat,lng"
                     and one row per winning game sold in a store (online sales are only counted)
  meta.json          {"updatedAt", "lotto", "pension", "lottoStores", "pensionStores"}: latest rounds

It starts from the existing files (the first time: copies of the app's public/data CSVs; the store
file is built from scratch), asks www.dhlottery.co.kr only for rounds newer than what the files
hold, with the same endpoints and checks as the Android app's tools/update_history.py and
tools/collect_stores.py, one plain GET (no custom headers) every 3 seconds. Rows are only appended
once a round is settled, so a draw whose results are not final yet is picked up by a later run.
A file is never shrunk. Exits 0 without touching anything when nothing is new; prints what changed.
"""
import argparse
import datetime as dt
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://www.dhlottery.co.kr"
LOTTO_URL = BASE + "/lt645/selectPstLt645Info.do"
PENSION_LIST_URL = BASE + "/pt720/selectPstPt720WnList.do"
PENSION_INFO_URL = BASE + "/pt720/selectPstPt720WnInfo.do?srchPsltEpsd={}"
PENSION_QR_URL = "https://qr.dhlottery.co.kr/api/lottery/PENSION/draw/{}"
LOTTO_STORES_URL = BASE + "/wnprchsplcsrch/selectLtWnShp.do?srchWnShpRnk=all&srchLtEpsd={}"
PENSION_STORES_URL = BASE + "/wnprchsplcsrch/selectPtWnShp.do?srchWnShpRnk=all&srchLtEpsd={}"

LOTTO_HEADER = "round,date,n1,n2,n3,n4,n5,n6,bonus,w1,a1,w2,a2,w3,a3,w4,a4,w5,a5,auto,manual,semi,sales"
PENSION_HEADER = "round,date,group,digits,bonus,w1,w2,w3,w4,w5,w6,w7,wb"
ROUND_HEADER = "round,rank,method,id,name,address,region,lat,lng"
LOTTO_FIRST = dt.date(2002, 12, 7)
PENSION_FIRST = dt.date(2020, 5, 7)
KST = dt.timezone(dt.timedelta(hours=9))

STORE_ROUNDS = 52
FIRST_STORE_ROUND = 262
ONLINE_STORE_ID = "51100000"
PENSION_BONUS_RANK = 8
REQUEST_GAP_S = 3.0

REGIONS = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
           "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
LONG_REGION_PREFIXES = [("충청북", "충북"), ("충청남", "충남"), ("전라북", "전북"),
                        ("전라남", "전남"), ("경상북", "경북"), ("경상남", "경남")]
SPACES = re.compile(r"[ \t\n\x0b\f\r]+")
BLOCK = re.compile(r"^#\s*(lotto|pension)\s+round=(\d+)")


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ---- HTTP: plain GETs, at most one every REQUEST_GAP_S seconds ----

class NotJson(Exception):
    pass


_last_request = [0.0]


def get_json(url, tries=3):
    last = None
    for attempt in range(tries):
        wait = _last_request[0] + REQUEST_GAP_S - time.monotonic()
        if attempt:
            wait = max(wait, 2 ** attempt + random.random())
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.monotonic()
        try:
            with urllib.request.urlopen(url, timeout=25) as resp:
                body = resp.read().decode("utf-8", errors="replace").strip()
            if not body.startswith("{") and not body.startswith("["):
                raise NotJson(body[:80])
            return json.loads(body)
        except (urllib.error.URLError, TimeoutError, ConnectionError, NotJson, json.JSONDecodeError, OSError) as e:
            last = e
            log(f"  retry {attempt + 1}/{tries} {url}: {e}")
    raise RuntimeError(f"GET failed: {url}: {last}")


def rows_of(root):
    """The rows at data.list / data.result / data / list (as the app's parsers accept)."""
    if isinstance(root, list):
        return root
    if isinstance(root, dict):
        data = root.get("data")
        if isinstance(data, dict):
            for k in ("list", "result"):
                if isinstance(data.get(k), list):
                    return data[k]
            return None
        if isinstance(data, list):
            return data
        if isinstance(root.get("list"), list):
            return root["list"]
    return None


def num(v):
    if v is None or isinstance(v, bool):
        return None
    try:
        return int(float(str(v).replace(",", "").strip()))
    except ValueError:
        return None


def iso(ymd):
    d = "".join(ch for ch in str(ymd or "") if ch.isdigit())
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else None


def digits6(v):
    s = str(v if v is not None else "").strip()
    s = s.zfill(6) if s.isdigit() else ""
    return s if len(s) == 6 else None


# ---- Files ----

def read_lines(path):
    return [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def last_round(path, header):
    if not path.exists():
        raise SystemExit(f"{path} is missing: copy it from the app's public/data/ first")
    lines = read_lines(path)
    if not lines or lines[0] != header:
        raise SystemExit(f"{path}: unexpected header")
    rounds = [int(ln.split(",")[0]) for ln in lines[1:]]
    if rounds != list(range(1, len(rounds) + 1)):
        raise SystemExit(f"{path}: rounds are not 1..{len(rounds)} in order")
    return rounds[-1] if rounds else 0


def write_atomic(path, text):
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == text:
        return False
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
    return True


def append_rows(path, rows):
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    new = text + "".join(r + "\n" for r in rows)
    if len(new) < len(text):
        raise SystemExit(f"{path}: refusing to shrink the file")
    write_atomic(path, new)


# ---- Lotto 6/45 (same checks as tools/update_history.py) ----

def lotto_row(item, r):
    """CSV line for round r, or None when the item is incomplete or its prizes are not settled."""
    if num(item.get("ltEpsd")) != r:
        return None
    date = iso(item.get("ltRflYmd"))
    if date != (LOTTO_FIRST + dt.timedelta(weeks=r - 1)).isoformat():
        log(f"lotto {r}: date {date} does not match the calendar")
        return None
    nums = [num(item.get(f"tm{i}WnNo")) for i in range(1, 7)]
    bonus = num(item.get("bnsWnNo"))
    if None in nums or bonus is None:
        return None
    if len(set(nums + [bonus])) != 7 or not all(1 <= n <= 45 for n in nums + [bonus]):
        log(f"lotto {r}: invalid numbers {nums} + {bonus}")
        return None
    cells = [str(r), date, *map(str, sorted(nums)), str(bonus)]
    for k in range(1, 6):
        w, a = num(item.get(f"rnk{k}WnNope")), num(item.get(f"rnk{k}WnAmt"))
        if w is None or a is None or w < 0 or a < 0:
            return None
        cells += [str(w), str(a)]
    # Fifth prize always has winners once the round is settled.
    if num(item.get("rnk5WnNope")) in (None, 0):
        log(f"lotto {r}: prizes not settled yet")
        return None
    split = [num(item.get(f"winType{i}")) for i in (1, 2, 3)]
    if None in split or sum(split) != num(item.get("rnk1WnNope")):
        split = ["", "", ""]
    sales = num(item.get("wholEpsdSumNtslAmt"))
    cells += [str(x) for x in split] + [str(sales) if sales and sales > 0 else ""]
    return ",".join(cells)


def update_lotto(path, changes):
    have = last_round(path, LOTTO_HEADER)
    latest_rows = rows_of(get_json(LOTTO_URL)) or []
    latest = max((num(x.get("ltEpsd")) or 0 for x in latest_rows if isinstance(x, dict)), default=0)
    if latest <= 0:
        raise RuntimeError("lotto: latest round not found")
    log(f"lotto: have {have}, latest {latest}")
    new = []
    for r in range(have + 1, latest + 1):
        items = [x for x in (rows_of(get_json(f"{LOTTO_URL}?srchLtEpsd={r}")) or []) if isinstance(x, dict)]
        row = next((lotto_row(x, r) for x in items if num(x.get("ltEpsd")) == r), None)
        if row is None:
            log(f"lotto {r}: not ready, stopping")
            break
        new.append(row)
    if new:
        append_rows(path, new)
        changes.append(f"{path.name}: +{len(new)} round(s) {have + 1}..{have + len(new)}")


# ---- 연금복권720+ (same checks as tools/update_history.py) ----

def pension_winners(r):
    """Winners of ranks 1..7 then the bonus, or None while the round is not settled."""
    counts = {}
    for x in rows_of(get_json(PENSION_INFO_URL.format(r))) or []:
        if not isinstance(x, dict):
            continue
        epsd = num(x.get("ltEpsd"))
        if epsd is not None and epsd != r:
            continue
        rank, n = num(x.get("wnRnk")), num(x.get("wnTotalCnt"))
        if rank in range(1, 9) and n is not None and n >= 0:
            counts[rank] = n
    if any(k not in counts for k in range(1, 9)) or counts[7] <= 0:
        return None
    return [counts[k] for k in range(1, 9)]


def update_pension(path, changes):
    have = last_round(path, PENSION_HEADER)
    now = dt.datetime.now(KST)
    expected = (now - dt.datetime(2020, 5, 7, 19, 5, tzinfo=KST)).days // 7 + 1
    if have >= expected:
        log(f"pension: have {have}, calendar {expected}: up to date")
        return
    by_round = {}
    for x in rows_of(get_json(PENSION_LIST_URL)) or []:
        if not isinstance(x, dict):
            continue
        r = num(x.get("psltEpsd"))
        if r:
            by_round[r] = {"date": iso(x.get("psltRflYmd")), "group": num(x.get("wnBndNo")),
                           "digits": digits6(x.get("wnRnkVl")), "bonus": digits6(x.get("bnsRnkVl"))}
    latest = max([expected] + list(by_round))
    log(f"pension: have {have}, list up to {max(by_round, default=0)}, calendar {expected}")
    new = []
    for r in range(have + 1, latest + 1):
        d = by_round.get(r)
        if d is None:
            try:
                q = get_json(PENSION_QR_URL.format(r))
            except RuntimeError:
                q = {}
            no = str(q.get("drawNo") or "") if isinstance(q, dict) else ""
            if not isinstance(q, dict) or q.get("drawStatus") == "NOT_DRAWN" or len(no) != 7 or not no.isdigit():
                log(f"pension {r}: not drawn or not found, stopping")
                break
            d = {"date": iso(q.get("drawDate")), "group": int(no[0]), "digits": no[1:], "bonus": digits6(q.get("bonusNo"))}
        if d["date"] != (PENSION_FIRST + dt.timedelta(weeks=r - 1)).isoformat():
            log(f"pension {r}: date {d['date']} does not match the calendar, stopping")
            break
        if d["group"] not in range(1, 6) or not d["digits"] or not d["bonus"]:
            log(f"pension {r}: invalid numbers {d}, stopping")
            break
        winners = pension_winners(r)
        if winners is None:
            log(f"pension {r}: winner counts not settled yet, stopping")
            break
        new.append(",".join([str(r), d["date"], str(d["group"]), d["digits"], d["bonus"], *map(str, winners)]))
    if new:
        append_rows(path, new)
        changes.append(f"{path.name}: +{len(new)} round(s) {have + 1}..{have + len(new)}")


# ---- Winner stores (same rules as StoreData.parseRound / parsePensionRound) ----

def clean(s):
    return SPACES.sub(" ", s).strip() if isinstance(s, str) else ""


def text(row, key):
    v = row.get(key)
    if v is None or isinstance(v, (dict, list)):
        return None
    if isinstance(v, bool):
        v = "true" if v else "false"
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = str(v).strip()
    return s or None


def coordinate(v, lo, hi):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if lo <= f <= hi else None


def normalize_region(raw):
    if raw is None:
        return ""
    s = SPACES.sub("", raw)
    if not s:
        return ""
    for prefix, short in LONG_REGION_PREFIXES:
        if s.startswith(prefix):
            return short
    for r in REGIONS:
        if s.startswith(r):
            return r
    return raw.strip()


def region_of(field, address):
    r = normalize_region(field)
    if r in REGIONS:
        return r
    words = SPACES.split(address.strip())
    fa = normalize_region(words[0]) if words else ""
    return fa if fa in REGIONS else r


def method_of(code, txt):
    c = (code or "").strip().upper()
    if c == "Q":
        return "AUTO"
    if c == "M":
        return "MANUAL"
    if c == "B":
        return "SEMI_AUTO"
    return {"자동": "AUTO", "수동": "MANUAL", "반자동": "SEMI_AUTO"}.get((txt or "").strip(), "")


def lotto_rank(row):
    return {1: 1, 2: 2}.get(num(text(row, "wnShpRnk")))


def pension_rank(row):
    return {1: 1, 2: 2, 21: PENSION_BONUS_RANK}.get(num(text(row, "wnShpRnk")))


def csv_cell(v):
    s = str(v).replace("\n", " ").replace("\r", " ")
    return '"' + s.replace('"', '""') + '"' if ("," in s or '"' in s) else s


def store_block(game, r, rows, rank_of):
    """stores-recent.csv block for round r (StoreData.roundToCsv with the game in the comment)."""
    wins, online = [], {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        rank = rank_of(row)
        if rank is None:
            continue
        sid = text(row, "ltShpId")
        if not sid:
            continue
        if sid == ONLINE_STORE_ID:
            online[rank] = online.get(rank, 0) + 1
            continue
        address = clean(text(row, "shpAddr") or "")
        if not address:
            address = clean(" ".join(x for x in (text(row, "rdnmAddr"), text(row, "rdnmDtlAddr")) if x))
        if not address:
            address = clean(text(row, "befAddr") or "")
        name = clean(text(row, "shpNm") or text(row, "tradNm") or text(row, "conmNm") or "")
        lat = coordinate(text(row, "shpLat"), 30.0, 45.0)
        lng = coordinate(text(row, "shpLot"), 120.0, 135.0)
        wins.append([str(r), str(rank), method_of(text(row, "atmtPsvYn"), text(row, "atmtPsvYnTxt")), sid, name,
                     address, region_of(text(row, "region"), address),
                     repr(lat) if lat is not None else "", repr(lng) if lng is not None else ""])
    if not wins and not online:
        return None
    head = f"# {game} round={r}" + "".join(f" online{k}={online[k]}" for k in sorted(online))
    return "\n".join([head, ROUND_HEADER] + [",".join(csv_cell(c) for c in w) for w in wins]) + "\n"


def read_blocks(path):
    blocks = {"lotto": {}, "pension": {}}
    if not path.exists():
        return blocks
    game, r, lines = None, None, []

    def flush():
        if game and r is not None:
            blocks[game][r] = "\n".join(lines) + "\n"

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        m = BLOCK.match(line.strip())
        if m:
            flush()
            game, r, lines = m.group(1), int(m.group(2)), [line.strip()]
        elif game:
            lines.append(line)
    flush()
    return blocks


def update_stores(path, lotto_latest, pension_latest, changes):
    blocks = read_blocks(path)
    before = {g: len(b) for g, b in blocks.items()}
    added = {"lotto": [], "pension": []}
    failed = False
    for game, latest, url, rank_of in (
        ("lotto", lotto_latest, LOTTO_STORES_URL, lotto_rank),
        ("pension", pension_latest, PENSION_STORES_URL, pension_rank),
    ):
        have = blocks[game]
        first = max(latest - STORE_ROUNDS + 1, FIRST_STORE_ROUND if game == "lotto" else 1)
        newest = max(have, default=0)
        wanted = [r for r in range(max(first, 1), latest + 1) if r not in have]
        if not wanted:
            log(f"stores {game}: have {first}..{latest}")
            continue
        log(f"stores {game}: fetching {len(wanted)} round(s) {wanted[0]}..{wanted[-1]}")
        for r in wanted:
            try:
                root = get_json(url.format(r))
            except RuntimeError as e:
                log(f"stores {game} {r}: {e}")
                failed = True
                break
            rows = rows_of(root)
            if rows is None:
                log(f"stores {game} {r}: no list in the response, stopping")
                failed = True
                break
            block = store_block(game, r, rows, rank_of)
            if block is None:
                if r > newest:
                    log(f"stores {game} {r}: not posted yet, stopping")
                    break
                log(f"stores {game} {r}: empty, skipped")
                continue
            have[r] = block
            added[game].append(r)
    dropped = {}
    for game, have in blocks.items():
        keep = sorted(have)[-STORE_ROUNDS:]
        dropped[game] = len(have) - len(keep)
        blocks[game] = {r: have[r] for r in keep}
        if len(blocks[game]) < min(before[game], STORE_ROUNDS):
            raise SystemExit(f"{path}: refusing to keep fewer {game} rounds than before")
    if added["lotto"] or added["pension"]:
        out = "".join(blocks["lotto"][r] for r in sorted(blocks["lotto"]))
        out += "".join(blocks["pension"][r] for r in sorted(blocks["pension"]))
        if write_atomic(path, out):
            parts = [f"{g} +{len(a)} ({a[0]}..{a[-1]})" for g, a in added.items() if a]
            parts += [f"{g} -{n} old" for g, n in dropped.items() if n]
            changes.append(f"{path.name}: " + ", ".join(parts))
    return (max(blocks["lotto"], default=0), max(blocks["pension"], default=0)), failed


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", type=Path, default=Path("data/lotto-sage"), help="output folder (default: data/lotto-sage)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when a request to the official site failed")
    args = ap.parse_args()
    out = args.dir
    out.mkdir(parents=True, exist_ok=True)
    lotto_csv, pension_csv = out / "lotto645.csv", out / "pension720.csv"
    stores_csv, meta_json = out / "stores-recent.csv", out / "meta.json"

    changes, failed = [], False
    for name, fn, path in (("lotto", update_lotto, lotto_csv), ("pension", update_pension, pension_csv)):
        try:
            fn(path, changes)
        except RuntimeError as e:
            log(f"{name}: {e}")
            failed = True

    lotto_latest = last_round(lotto_csv, LOTTO_HEADER)
    pension_latest = last_round(pension_csv, PENSION_HEADER)
    (lotto_stores, pension_stores), stores_failed = update_stores(stores_csv, lotto_latest, pension_latest, changes)
    failed = failed or stores_failed

    meta = {"lotto": lotto_latest, "pension": pension_latest, "lottoStores": lotto_stores, "pensionStores": pension_stores}
    old = {}
    if meta_json.exists():
        try:
            old = json.loads(meta_json.read_text(encoding="utf-8"))
        except ValueError:
            old = {}
    if changes or any(old.get(k) != v for k, v in meta.items()):
        meta = {"updatedAt": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **meta}
        write_atomic(meta_json, json.dumps(meta, ensure_ascii=False) + "\n")
        changes.append(f"{meta_json.name}: {json.dumps(meta, ensure_ascii=False)}")

    if changes:
        print("Updated " + str(out) + ":")
        for c in changes:
            print("  " + c)
    else:
        print("No new data.")
    if failed:
        log("warning: some requests to the official site failed; the next run will retry")
    return 1 if (failed and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
