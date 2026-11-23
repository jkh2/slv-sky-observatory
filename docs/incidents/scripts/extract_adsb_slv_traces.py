#!/usr/bin/env python3
"""Filter adsblol/globe_history_2026 traces to the San Luis Valley window
and compute azimuth/elevation from public reference points.

Authorship: authored by an AI agent, SLV Sky Observatory Investigator
(a Grok Bot AI research agent created to serve as an external investigative
contributor/journalist), submitted via the repository owner's GitHub account
(jkh2) with the owner's permission. Not a product of the project's resident AI.

Source dataset: adsblol/globe_history_2026, release v2026.11.22-planes-readsb-prod-0
License: ODbL 1.0 (https://opendatacommons.org/licenses/odbl/1.0/).
Trace layout: wiedehopf/readsb README-json.md (timestamp + relative seconds).

This script reads a (possibly split) tar archive on stdin or from given part
paths, and writes a filtered extract. It does not keep the bulk archive.
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import math
import sys
import tarfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

# --- windows and reference points (documented in the incident file) ---

# UTC window: 22 Nov 2026 03:00-03:30 = 21 Nov 2026 20:00-20:30 MST
T_START = 1795316400.0
T_END = 1795318200.0
MST = timezone(timedelta(hours=-7))

# Bounding box: SLV plus surrounding sky visible from Alamosa
LAT_MIN, LAT_MAX = 37.0, 38.3
# West longitudes stored as negative
LON_MIN, LON_MAX = -106.7, -105.3

# Ephemeris / town reference (not a witness pin)
REF = {
    "name": "alamosa_reference",
    "lat": 37.47,
    "lon": -105.87,
    "elev_m": 2300.0,
    "note": "Public Alamosa-area reference used for az/el; not an observer pin.",
}

# Approximate observer east of Alamosa on US-160 (not a witness pin)
OBS_EAST = {
    "name": "approx_observer_east_us160",
    "lat": 37.47,
    "lon": -105.80,
    "elev_m": 2300.0,
    "note": "Approximate area only: east of Alamosa on US-160, looking west. Not a measured witness coordinate.",
}

# Public Loaf 'N Jug / US-160 & CO-17 junction (from public listings)
JUNCTION = {
    "name": "us160_co17_loaf_n_jug_area",
    "lat": 37.47358,
    "lon": -105.856805,
    "elev_m": 2300.0,
    "note": "Public commercial/park junction (Loaf 'N Jug / Rio Grande Farm Park area). Approximate public coordinates.",
}

WEST_AZ_MIN, WEST_AZ_MAX = 200.0, 320.0
LOW_ELEV_DEG = 10.0
# Angular proximity to the junction bearing, from the approximate east observer
NEAR_BEARING_DEG = 15.0

# WGS84
_A = 6378137.0
_F = 1.0 / 298.257223563
_E2 = _F * (2.0 - _F)
FT_TO_M = 0.3048


def _llh_to_ecef(lat_deg: float, lon_deg: float, h_m: float) -> tuple[float, float, float]:
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    sl, cl = math.sin(lat), math.cos(lat)
    so, co = math.sin(lon), math.cos(lon)
    n = _A / math.sqrt(1.0 - _E2 * sl * sl)
    x = (n + h_m) * cl * co
    y = (n + h_m) * cl * so
    z = (n * (1.0 - _E2) + h_m) * sl
    return x, y, z


def _ecef_to_enu(x, y, z, lat0, lon0, x0, y0, z0) -> tuple[float, float, float]:
    lat = math.radians(lat0)
    lon = math.radians(lon0)
    sl, cl = math.sin(lat), math.cos(lat)
    so, co = math.sin(lon), math.cos(lon)
    dx, dy, dz = x - x0, y - y0, z - z0
    east = -so * dx + co * dy
    north = -sl * co * dx - sl * so * dy + cl * dz
    up = cl * co * dx + cl * so * dy + sl * dz
    return east, north, up


def az_el_range(lat, lon, h_m, origin: dict) -> Optional[dict]:
    """Geodetic azimuth (0=N, 90=E), elevation, and slant range. No refraction."""
    if lat is None or lon is None or h_m is None:
        return None
    x0, y0, z0 = origin["_ecef"]
    x, y, z = _llh_to_ecef(lat, lon, h_m)
    east, north, up = _ecef_to_enu(x, y, z, origin["lat"], origin["lon"], x0, y0, z0)
    horiz = math.hypot(east, north)
    slant = math.sqrt(east * east + north * north + up * up)
    if slant <= 1.0:
        return {"az_deg": None, "el_deg": 90.0, "range_km": slant / 1000.0, "ground_range_km": horiz / 1000.0}
    az = (math.degrees(math.atan2(east, north)) + 360.0) % 360.0
    el = math.degrees(math.atan2(up, horiz))
    return {"az_deg": az, "el_deg": el, "range_km": slant / 1000.0, "ground_range_km": horiz / 1000.0}


def ang_diff(a: float, b: float) -> float:
    """Smallest absolute difference between two bearings, degrees."""
    return abs((a - b + 180.0) % 360.0 - 180.0)


def prepare_origin(o: dict) -> dict:
    out = dict(o)
    out["_ecef"] = _llh_to_ecef(o["lat"], o["lon"], o["elev_m"])
    return out


def parse_alt_m(pt) -> tuple[Optional[float], str]:
    """Return (height AMSL meters, source tag). Prefer geometric altitude when present."""
    flags = pt[6] if len(pt) > 6 and pt[6] is not None else 0
    alt = pt[3] if len(pt) > 3 else None
    geom = pt[10] if len(pt) > 10 else None
    if geom is not None and isinstance(geom, (int, float)):
        return geom * FT_TO_M, "geom_alt"
    if alt == "ground":
        return None, "ground"
    if alt is not None and isinstance(alt, (int, float)):
        kind = "geom_alt_as_baro" if (flags & 8) else "baro_alt"
        return alt * FT_TO_M, kind
    return None, "missing"


def parse_time(base_ts: float, pt) -> Optional[float]:
    if not pt:
        return None
    try:
        return float(base_ts) + float(pt[0])
    except (TypeError, ValueError, IndexError):
        return None


def in_bbox(lat, lon) -> bool:
    return lat is not None and lon is not None and LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX


def in_time(t) -> bool:
    return t is not None and T_START <= t <= T_END


def iso_mst(t: float) -> str:
    return datetime.fromtimestamp(t, tz=MST).strftime("%Y-%m-%d %H:%M:%S MST")


def iso_utc(t: float) -> str:
    return datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def open_tar(parts: list[Path]):
    """Open a split tar as a stream without writing a concatenated copy."""
    if len(parts) == 1:
        return tarfile.open(parts[0], mode="r|*")
    # Concatenate via a generator file-like object
    return tarfile.open(fileobj=_ConcatReader(parts), mode="r|*")


class _ConcatReader(io.RawIOBase):
    def __init__(self, paths: list[Path]):
        self._files = [open(p, "rb") for p in paths]
        self._i = 0

    def readable(self) -> bool:
        return True

    def read(self, size: int = -1) -> bytes:
        if self._i >= len(self._files):
            return b""
        data = self._files[self._i].read(size)
        if data:
            return data
        self._files[self._i].close()
        self._i += 1
        return self.read(size)

    def readinto(self, b) -> int:
        chunk = self.read(len(b))
        n = len(chunk)
        b[:n] = chunk
        return n

    def close(self) -> None:
        for f in self._files:
            try:
                f.close()
            except Exception:
                pass
        super().close()


def maybe_decompress(raw: bytes) -> bytes:
    if raw[:2] == b"\x1f\x8b":
        return gzip.decompress(raw)
    return raw


def load_trace_bytes(raw: bytes) -> Optional[dict]:
    try:
        return json.loads(maybe_decompress(raw))
    except Exception:
        return None


def collect_identity(obj: dict, points: list) -> dict:
    icao = obj.get("icao") or obj.get("hex")
    reg = obj.get("r")
    typ = obj.get("t")
    desc = obj.get("desc")
    db_flags = obj.get("dbFlags") or 0
    callsigns = []
    sources = set()
    squawks = set()
    categories = set()
    for pt in points:
        if len(pt) > 9 and isinstance(pt[9], str) and pt[9]:
            sources.add(pt[9])
        if len(pt) > 8 and isinstance(pt[8], dict):
            d = pt[8]
            fl = d.get("flight")
            if isinstance(fl, str) and fl.strip():
                callsigns.append(fl.strip())
            if d.get("type"):
                sources.add(str(d["type"]))
            if d.get("squawk"):
                squawks.add(str(d["squawk"]))
            if d.get("category"):
                categories.add(str(d["category"]))
            if not typ and d.get("t"):
                typ = d.get("t")
            if not reg and d.get("r"):
                reg = d.get("r")
    # unique callsigns, preserve order
    seen = set()
    uniq_cs = []
    for c in callsigns:
        if c not in seen:
            seen.add(c)
            uniq_cs.append(c)
    hex_str = str(icao).lower() if icao is not None else None
    non_icao = bool(hex_str and str(hex_str).startswith("~"))
    return {
        "hex": hex_str,
        "registration": reg,
        "type": typ,
        "type_desc": desc,
        "callsigns": uniq_cs,
        "dbFlags": db_flags,
        "military_dbFlag": bool(db_flags & 1),
        "ladd_dbFlag": bool(db_flags & 8),
        "pia_dbFlag": bool(db_flags & 4),
        "non_icao_hex": non_icao,
        "position_sources": sorted(sources),
        "mlat_only": bool(sources) and all(s.startswith("mlat") for s in sources),
        "mlat_present": any("mlat" in s for s in sources),
        "squawks": sorted(squawks),
        "categories": sorted(categories),
        "no_callsign": not uniq_cs,
    }


def summarize_aircraft(obj: dict, in_window_pts: list, origins: dict, junction_az: float) -> dict:
    ident = collect_identity(obj, in_window_pts)
    times = []
    alts = []
    tracks = []
    speeds = []
    src_alt_kinds = set()
    ref_stats = []
    obs_stats = []

    for pt in in_window_pts:
        t = parse_time(obj["timestamp"], pt)
        lat, lon = pt[1], pt[2]
        h_m, alt_kind = parse_alt_m(pt)
        src_alt_kinds.add(alt_kind)
        gs = pt[4] if len(pt) > 4 else None
        trk = pt[5] if len(pt) > 5 else None
        flags = pt[6] if len(pt) > 6 and pt[6] is not None else 0
        stale = bool(flags & 1)
        rec = {
            "t": t,
            "lat": lat,
            "lon": lon,
            "alt_m": h_m,
            "alt_ft": (h_m / FT_TO_M) if h_m is not None else None,
            "alt_kind": alt_kind,
            "gs_kt": gs,
            "track_deg": trk,
            "stale": stale,
        }
        if t is not None:
            times.append(t)
        if h_m is not None:
            alts.append(h_m / FT_TO_M)
        if isinstance(trk, (int, float)):
            tracks.append(float(trk))
        if isinstance(gs, (int, float)):
            speeds.append(float(gs))

        for key, origin, bucket in (
            ("ref", origins["ref"], ref_stats),
            ("obs", origins["obs"], obs_stats),
        ):
            if h_m is None:
                continue
            geo = az_el_range(lat, lon, h_m, origin)
            if not geo:
                continue
            item = dict(rec)
            item.update(geo)
            item["in_west"] = geo["az_deg"] is not None and WEST_AZ_MIN <= geo["az_deg"] <= WEST_AZ_MAX
            item["low_elev"] = geo["el_deg"] is not None and 0.0 <= geo["el_deg"] < LOW_ELEV_DEG
            item["above_horizon"] = geo["el_deg"] is not None and geo["el_deg"] >= 0.0
            if key == "obs" and geo["az_deg"] is not None:
                item["az_sep_from_junction_bearing_deg"] = ang_diff(geo["az_deg"], junction_az)
                item["near_junction_bearing"] = item["az_sep_from_junction_bearing_deg"] <= NEAR_BEARING_DEG
            bucket.append(item)

    def _span(vals, nd=1):
        if not vals:
            return None
        return {"min": round(min(vals), nd), "max": round(max(vals), nd), "median": round(sorted(vals)[len(vals)//2], nd)}

    def _view_summary(rows: list, include_junction: bool) -> dict:
        if not rows:
            return {"n_with_geometry": 0}
        west = [r for r in rows if r.get("in_west")]
        west_low = [r for r in west if r.get("low_elev")]
        above = [r for r in rows if r.get("above_horizon")]
        # closest (min range) among points with geometry
        closest = min(rows, key=lambda r: r["range_km"])
        # highest elevation (most above horizon)
        highest = max(rows, key=lambda r: r["el_deg"])
        # most westerly? not needed
        out = {
            "n_with_geometry": len(rows),
            "any_in_west_az_200_320": bool(west),
            "any_in_west_and_low_elev_lt_10": bool(west_low),
            "any_above_horizon": bool(above),
            "az_deg": _span([r["az_deg"] for r in rows if r["az_deg"] is not None], 1),
            "el_deg": _span([r["el_deg"] for r in rows], 2),
            "range_km": _span([r["range_km"] for r in rows], 1),
            "closest": {
                "time_mst": iso_mst(closest["t"]) if closest["t"] else None,
                "time_utc": iso_utc(closest["t"]) if closest["t"] else None,
                "az_deg": None if closest["az_deg"] is None else round(closest["az_deg"], 1),
                "el_deg": round(closest["el_deg"], 2),
                "range_km": round(closest["range_km"], 1),
                "alt_ft": None if closest["alt_ft"] is None else round(closest["alt_ft"]),
                "in_west": closest["in_west"],
                "low_elev": closest["low_elev"],
            },
            "highest_elevation": {
                "time_mst": iso_mst(highest["t"]) if highest["t"] else None,
                "time_utc": iso_utc(highest["t"]) if highest["t"] else None,
                "az_deg": None if highest["az_deg"] is None else round(highest["az_deg"], 1),
                "el_deg": round(highest["el_deg"], 2),
                "range_km": round(highest["range_km"], 1),
                "alt_ft": None if highest["alt_ft"] is None else round(highest["alt_ft"]),
                "in_west": highest["in_west"],
                "low_elev": highest["low_elev"],
            },
        }
        if include_junction:
            near = [r for r in rows if r.get("near_junction_bearing")]
            best = min(rows, key=lambda r: r.get("az_sep_from_junction_bearing_deg", 999))
            out["any_near_junction_bearing_15deg"] = bool(near)
            out["min_az_sep_from_junction_bearing_deg"] = round(best.get("az_sep_from_junction_bearing_deg", 999), 1)
            out["at_min_az_sep"] = {
                "time_mst": iso_mst(best["t"]) if best["t"] else None,
                "az_deg": None if best["az_deg"] is None else round(best["az_deg"], 1),
                "el_deg": round(best["el_deg"], 2),
                "range_km": round(best["range_km"], 1),
                "alt_ft": None if best["alt_ft"] is None else round(best["alt_ft"]),
                "in_west": best["in_west"],
                "low_elev": best["low_elev"],
            }
        return out

    # representative ground track: median of in-window tracks
    ident.update({
        "n_points_in_window_and_bbox": len(in_window_pts),
        "time_first_mst": iso_mst(min(times)) if times else None,
        "time_last_mst": iso_mst(max(times)) if times else None,
        "time_first_utc": iso_utc(min(times)) if times else None,
        "time_last_utc": iso_utc(max(times)) if times else None,
        "duration_s": (round(max(times) - min(times), 1) if len(times) >= 2 else 0.0),
        "altitude_ft": _span(alts, 0) if alts else None,
        "ground_track_deg": _span(tracks, 1) if tracks else None,
        "ground_speed_kt": _span(speeds, 1) if speeds else None,
        "altitude_kinds": sorted(src_alt_kinds),
        "from_alamosa_reference": _view_summary(ref_stats, include_junction=False),
        "from_approx_observer_east_us160": _view_summary(obs_stats, include_junction=True),
    })
    # slim point list for the extract (every in-window bbox point, with both geometries)
    slim = []
    ref_by_t = {round(r["t"], 3): r for r in ref_stats if r.get("t") is not None}
    obs_by_t = {round(r["t"], 3): r for r in obs_stats if r.get("t") is not None}
    for pt in in_window_pts:
        t = parse_time(obj["timestamp"], pt)
        key = None if t is None else round(t, 3)
        rref = ref_by_t.get(key) if key is not None else None
        robs = obs_by_t.get(key) if key is not None else None
        h_m, alt_kind = parse_alt_m(pt)
        slim.append({
            "t_utc": iso_utc(t) if t else None,
            "t_mst": iso_mst(t) if t else None,
            "lat": pt[1],
            "lon": pt[2],
            "alt_ft": None if h_m is None else round(h_m / FT_TO_M),
            "alt_kind": alt_kind,
            "gs_kt": pt[4] if len(pt) > 4 else None,
            "track_deg": pt[5] if len(pt) > 5 else None,
            "source": pt[9] if len(pt) > 9 else None,
            "ref_az_deg": None if not rref or rref["az_deg"] is None else round(rref["az_deg"], 1),
            "ref_el_deg": None if not rref else round(rref["el_deg"], 2),
            "ref_range_km": None if not rref else round(rref["range_km"], 1),
            "obs_az_deg": None if not robs or robs["az_deg"] is None else round(robs["az_deg"], 1),
            "obs_el_deg": None if not robs else round(robs["el_deg"], 2),
            "obs_range_km": None if not robs else round(robs["range_km"], 1),
            "obs_az_sep_junction_deg": None if not robs else (None if "az_sep_from_junction_bearing_deg" not in robs else round(robs["az_sep_from_junction_bearing_deg"], 1)),
        })
    ident["points"] = slim
    return ident


def process_archive(parts: list[Path], out_dir: Path) -> dict:
    origins = {
        "ref": prepare_origin(REF),
        "obs": prepare_origin(OBS_EAST),
    }
    junc = prepare_origin(JUNCTION)
    # Bearing from approximate east observer to the public junction
    # Use a nominal 10 m tower/building height so the point is not identical-height-only.
    geo_j = az_el_range(JUNCTION["lat"], JUNCTION["lon"], JUNCTION["elev_m"] + 10.0, origins["obs"])
    junction_az = geo_j["az_deg"]
    junction_dist_km = geo_j["range_km"]

    matches = []
    n_members = 0
    n_trace_files = 0
    n_parse_fail = 0
    n_no_points = 0

    tar = open_tar(parts)
    try:
        for member in tar:
            n_members += 1
            if not member.isfile():
                continue
            name = member.name.replace("\\", "/")
            # traces live under traces/ or .../traces/xx/trace_full_HEX.json(.gz)
            base = name.split("/")[-1]
            if not (base.startswith("trace_") or "/traces/" in "/" + name):
                continue
            if not (base.endswith(".json") or base.endswith(".json.gz") or "trace_" in base):
                continue
            n_trace_files += 1
            f = tar.extractfile(member)
            if f is None:
                n_parse_fail += 1
                continue
            obj = load_trace_bytes(f.read())
            if not obj or "trace" not in obj or "timestamp" not in obj:
                n_parse_fail += 1
                continue
            pts = []
            for pt in obj["trace"] or []:
                if not isinstance(pt, list) or len(pt) < 3:
                    continue
                t = parse_time(obj["timestamp"], pt)
                if not in_time(t):
                    continue
                if not in_bbox(pt[1], pt[2]):
                    continue
                pts.append(pt)
            if not pts:
                n_no_points += 1
                continue
            matches.append(summarize_aircraft(obj, pts, origins, junction_az))
            if n_trace_files % 2000 == 0:
                print(
                    f"... scanned {n_trace_files} trace files, {len(matches)} matches so far",
                    file=sys.stderr,
                    flush=True,
                )
    finally:
        tar.close()

    # Sort: western first, then closest approach to the reference
    def _sort_key(a):
        west = a["from_alamosa_reference"].get("any_in_west_az_200_320")
        rng = (a["from_alamosa_reference"].get("range_km") or {}).get("min") or 9999
        return (0 if west else 1, rng)

    matches.sort(key=_sort_key)

    # Strip bulky points into a sidecar per aircraft for the summary? Keep points
    # in the extract file; also write a compact summary without every point.
    compact = []
    for a in matches:
        c = {k: v for k, v in a.items() if k != "points"}
        compact.append(c)

    summary = {
        "dataset": {
            "name": "adsblol/globe_history_2026",
            "release": "v2026.11.22-planes-readsb-prod-0",
            "url": "https://github.com/adsblol/globe_history_2026/releases/tag/v2026.11.22-planes-readsb-prod-0",
            "license": "ODbL 1.0",
            "license_url": "https://opendatacommons.org/licenses/odbl/1.0/",
        },
        "method": {
            "time_window_utc": ["2026-11-22 03:00:00 UTC", "2026-11-22 03:30:00 UTC"],
            "time_window_mst": ["2026-11-21 20:00:00 MST", "2026-11-21 20:30:00 MST"],
            "bbox_lat": [LAT_MIN, LAT_MAX],
            "bbox_lon": [LON_MIN, LON_MAX],
            "alamosa_reference": {k: v for k, v in REF.items()},
            "approx_observer_east_us160": {k: v for k, v in OBS_EAST.items()},
            "junction_us160_co17": {k: v for k, v in JUNCTION.items()},
            "junction_bearing_from_approx_observer_deg": None if junction_az is None else round(junction_az, 1),
            "junction_distance_from_approx_observer_km": None if junction_dist_km is None else round(junction_dist_km, 2),
            "west_azimuth_window_deg": [WEST_AZ_MIN, WEST_AZ_MAX],
            "low_elevation_threshold_deg": LOW_ELEV_DEG,
            "near_junction_bearing_threshold_deg": NEAR_BEARING_DEG,
            "geometry": "WGS84 ECEF to ENU; no atmospheric refraction. Geometric altitude preferred when present in the trace; otherwise barometric altitude (pressure altitude, not true height).",
            "trace_time": "Absolute time = JSON 'timestamp' (unix seconds) + per-point offset seconds, per readsb README-json.md.",
            "coverage_caveat": "This is a volunteer ADS-B/MLAT archive. Aircraft without a transponder, with ADS-B off, or outside receiver coverage (including some military flights) may be absent. Absence of a trace is not evidence that no aircraft was present.",
        },
        "scan": {
            "tar_members_seen": n_members,
            "trace_files_scanned": n_trace_files,
            "parse_failures": n_parse_fail,
            "trace_files_without_match": n_no_points,
            "matching_aircraft": len(matches),
        },
        "aircraft": compact,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / "slv_filtered_2026-11-22_0300-0330Z_summary.json"
    full_path = out_dir / "slv_filtered_2026-11-22_0300-0330Z_traces.json"
    csv_path = out_dir / "slv_filtered_2026-11-22_0300-0330Z.csv"

    summary_path.write_text(json.dumps(summary, indent=2))
    full_path.write_text(json.dumps({"meta": summary["method"], "dataset": summary["dataset"], "aircraft": matches}, indent=2))

    # CSV one row per aircraft
    import csv
    fields = [
        "hex", "callsigns", "registration", "type", "type_desc",
        "time_first_mst", "time_last_mst", "duration_s",
        "alt_ft_min", "alt_ft_max", "track_deg_median", "gs_kt_median",
        "military_dbFlag", "no_callsign", "mlat_only", "position_sources",
        "ref_any_west", "ref_any_west_low", "ref_az_min", "ref_az_max",
        "ref_el_min", "ref_el_max", "ref_range_km_min",
        "obs_min_az_sep_junction_deg", "obs_any_near_junction_bearing_15deg",
    ]
    with csv_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for a in compact:
            ref = a.get("from_alamosa_reference") or {}
            obs = a.get("from_approx_observer_east_us160") or {}
            alt = a.get("altitude_ft") or {}
            trk = a.get("ground_track_deg") or {}
            gs = a.get("ground_speed_kt") or {}
            w.writerow({
                "hex": a.get("hex"),
                "callsigns": " ".join(a.get("callsigns") or []),
                "registration": a.get("registration"),
                "type": a.get("type"),
                "type_desc": a.get("type_desc"),
                "time_first_mst": a.get("time_first_mst"),
                "time_last_mst": a.get("time_last_mst"),
                "duration_s": a.get("duration_s"),
                "alt_ft_min": (alt or {}).get("min"),
                "alt_ft_max": (alt or {}).get("max"),
                "track_deg_median": (trk or {}).get("median"),
                "gs_kt_median": (gs or {}).get("median"),
                "military_dbFlag": a.get("military_dbFlag"),
                "no_callsign": a.get("no_callsign"),
                "mlat_only": a.get("mlat_only"),
                "position_sources": " ".join(a.get("position_sources") or []),
                "ref_any_west": ref.get("any_in_west_az_200_320"),
                "ref_any_west_low": ref.get("any_in_west_and_low_elev_lt_10"),
                "ref_az_min": (ref.get("az_deg") or {}).get("min"),
                "ref_az_max": (ref.get("az_deg") or {}).get("max"),
                "ref_el_min": (ref.get("el_deg") or {}).get("min"),
                "ref_el_max": (ref.get("el_deg") or {}).get("max"),
                "ref_range_km_min": (ref.get("range_km") or {}).get("min"),
                "obs_min_az_sep_junction_deg": obs.get("min_az_sep_from_junction_bearing_deg"),
                "obs_any_near_junction_bearing_15deg": obs.get("any_near_junction_bearing_15deg"),
            })

    summary["output_files"] = {
        "summary": str(summary_path),
        "traces": str(full_path),
        "csv": str(csv_path),
    }
    return summary


def main(argv: Optional[Iterable[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("parts", nargs="+", type=Path, help="tar part paths in order (.aa, .ab, ...)")
    ap.add_argument("--out", type=Path, required=True, help="output directory for the filtered extract")
    args = ap.parse_args(argv)
    parts = [p.resolve() for p in args.parts]
    for p in parts:
        if not p.is_file():
            print(f"missing part: {p}", file=sys.stderr)
            return 2
        print(f"part {p.name}: {p.stat().st_size} bytes", file=sys.stderr)
    print("scanning traces...", file=sys.stderr, flush=True)
    summary = process_archive(parts, args.out.resolve())
    print(json.dumps({
        "scan": summary["scan"],
        "junction_bearing_from_approx_observer_deg": summary["method"]["junction_bearing_from_approx_observer_deg"],
        "junction_distance_from_approx_observer_km": summary["method"]["junction_distance_from_approx_observer_km"],
        "n_aircraft": summary["scan"]["matching_aircraft"],
        "hexes": [a["hex"] for a in summary["aircraft"]],
        "western_from_reference": [
            a["hex"] for a in summary["aircraft"]
            if a["from_alamosa_reference"].get("any_in_west_az_200_320")
        ],
        "output": summary["output_files"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
