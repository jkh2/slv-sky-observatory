#!/usr/bin/env python3
"""Sky, twilight, sidereal-drift, and satellite-pass context for the
21 Nov 2026 ~20:15 MST westward-lights incident (Alamosa, CO).

Authorship: authored by an AI agent, SLV Sky Observatory Investigator
(a Grok Bot AI research agent created to serve as an external investigative
contributor/journalist), submitted via the repository owner's GitHub account
(jkh2) with the owner's permission. Not a product of the project's resident AI.

Calculation point is a public town-area reference, not an exact observer pin.
TLEs used for the committed JSON were retrieved on 22 Nov 2026 and used to
reconstruct the previous evening; see epoch caveats in the incident file.

This script is provided so the computation can be reproduced. The committed
JSON under docs/incidents/data/2026-11-21-westward-lights/ is the run of
record. Default --ephem-dir is a local ephemeris/TLE directory you supply
(JPL DE421 and CelesTrak GP files are not committed).
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from skyfield.api import EarthSatellite, Star, load, wgs84
from skyfield.almanac import find_discrete, risings_and_settings, dark_twilight_day
from skyfield import almanac
from skyfield.magnitudelib import planetary_magnitude

HERE = Path(__file__).resolve().parent
# Defaults: ephemeris/TLEs are supplied by the operator (not committed).
# Output defaults to the committed data directory beside this script when
# the repo layout is docs/incidents/scripts/ + docs/incidents/data/...
DATA = Path("ephem")  # replaced in main() from --ephem-dir
OUT = HERE.parent / "data" / "2026-11-21-westward-lights"

# Public calculation point: Alamosa area (brief). Not an exact witness location.
LAT, LON, ELEV_M = 37.47, -105.87, 2300.0
WEST_AZ_MIN, WEST_AZ_MAX = 200.0, 320.0
MST = timezone(timedelta(hours=-7), name="MST")

# Named bright stars, J2000, V mag (standard catalog values).
BRIGHT_STARS = {
    "Sirius":      (6 + 45/60 + 8.9/3600, -(16 + 42/60 + 58/3600), -1.46),
    "Canopus":     (6 + 23/60 + 57.1/3600, -(52 + 41/60 + 44/3600), -0.74),
    "Arcturus":    (14 + 15/60 + 39.7/3600, 19 + 10/60 + 57/3600, -0.05),
    "Vega":        (18 + 36/60 + 56.3/3600, 38 + 47/60 + 1/3600, 0.03),
    "Capella":     (5 + 16/60 + 41.4/3600, 45 + 59/60 + 53/3600, 0.08),
    "Rigel":       (5 + 14/60 + 32.3/3600, -(8 + 12/60 + 6/3600), 0.13),
    "Procyon":     (7 + 39/60 + 18.1/3600, 5 + 13/60 + 30/3600, 0.34),
    "Betelgeuse":  (5 + 55/60 + 10.3/3600, 7 + 24/60 + 25/3600, 0.50),
    "Achernar":    (1 + 37/60 + 42.8/3600, -(57 + 14/60 + 12/3600), 0.46),
    "Altair":      (19 + 50/60 + 47.0/3600, 8 + 52/60 + 6/3600, 0.76),
    "Aldebaran":   (4 + 35/60 + 55.2/3600, 16 + 30/60 + 33/3600, 0.85),
    "Antares":     (16 + 29/60 + 24.4/3600, -(26 + 25/60 + 55/3600), 1.09),
    "Spica":       (13 + 25/60 + 11.6/3600, -(11 + 9/60 + 41/3600), 0.98),
    "Pollux":      (7 + 45/60 + 18.9/3600, 28 + 1/60 + 34/3600, 1.14),
    "Fomalhaut":   (22 + 57/60 + 39.0/3600, -(29 + 37/60 + 20/3600), 1.16),
    "Deneb":       (20 + 41/60 + 25.9/3600, 45 + 16/60 + 49/3600, 1.25),
    "Regulus":     (10 + 8/60 + 22.3/3600, 11 + 58/60 + 2/3600, 1.36),
    "Adhara":      (6 + 58/60 + 37.5/3600, -(28 + 58/60 + 20/3600), 1.50),
    "Castor":      (7 + 34/60 + 36.0/3600, 31 + 53/60 + 18/3600, 1.58),  # slightly fainter; include as near cutoff
    "Bellatrix":   (5 + 25/60 + 7.9/3600, 6 + 20/60 + 59/3600, 1.64),
    "Elnath":      (5 + 26/60 + 17.5/3600, 28 + 36/60 + 27/3600, 1.65),
    "Alnilam":     (5 + 36/60 + 12.8/3600, -(1 + 12/60 + 7/3600), 1.69),
}

# Approximate public peak positions for a western-horizon elevation estimate.
# Coordinates are widely published summit locations; used only for a rough
# geometric horizon angle, not as sighting pins.
WEST_PEAKS = [
    ("Bennett Peak (approx. published summit)", 37.483, -106.434, 4024),
    ("Conejos Peak (approx. published summit)", 37.288, -106.571, 4017),
]


def fmt_az(az):
    return f"{az:6.1f}°"


def fmt_alt(alt):
    return f"{alt:6.2f}°"


def horizon_angle(lat0, lon0, h0, lat1, lon1, h1):
    # Simple ellipsoidal-ish distance (haversine) + atan2 of height difference,
    # with a dip/curvature correction of d/(2R).
    R = 6371000.0
    p1, p2 = math.radians(lat0), math.radians(lat1)
    dphi = math.radians(lat1 - lat0)
    dl = math.radians(lon1 - lon0)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    dist = 2 * R * math.asin(math.sqrt(a))
    # geometric elevation, plus refraction ignored; subtract curvature
    elev = math.degrees(math.atan2((h1 - h0) - (dist**2)/(2*R), dist))
    bearing = math.degrees(math.atan2(
        math.sin(dl)*math.cos(p2),
        math.cos(p1)*math.sin(p2) - math.sin(p1)*math.cos(p2)*math.cos(dl)
    )) % 360
    return dist / 1000.0, bearing, elev


def load_tles(path):
    lines = Path(path).read_text(errors="replace").splitlines()
    sats = []
    i = 0
    while i < len(lines) - 2:
        name, l1, l2 = lines[i].strip(), lines[i+1].strip(), lines[i+2].strip()
        if l1.startswith("1 ") and l2.startswith("2 "):
            try:
                sats.append(EarthSatellite(l1, l2, name))
            except Exception:
                pass
            i += 3
        else:
            i += 1
    return sats


def tle_epoch_summary(sats, label):
    if not sats:
        return {"label": label, "n": 0}
    epochs = [s.epoch.utc_datetime().replace(tzinfo=timezone.utc) for s in sats]
    return {
        "label": label,
        "n": len(sats),
        "epoch_min": min(epochs).isoformat(),
        "epoch_max": max(epochs).isoformat(),
        "epoch_median": sorted(epochs)[len(epochs)//2].isoformat(),
    }


def az_alt(eph, body, topo, t):
    app = topo.at(t).observe(body).apparent()
    alt, az, _ = app.altaz()
    return az.degrees, alt.degrees, app


def main():
    import argparse
    global DATA, OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ephem-dir",
        type=Path,
        default=Path("ephem"),
        help="Directory containing skyfield-data/de421.bsp and TLE files visual.txt, stations.txt, starlink.txt",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=HERE.parent / "data" / "2026-11-21-westward-lights",
        help="Directory for sky_context_2026-11-21.json (defaults to the committed data path in this repo)",
    )
    args = parser.parse_args()
    DATA = args.ephem_dir
    OUT = args.out_dir
    OUT.mkdir(parents=True, exist_ok=True)
    ts = load.timescale()
    eph = load(str(DATA / "skyfield-data" / "de421.bsp"))
    earth, sun, moon = eph["earth"], eph["sun"], eph["moon"]
    planets = {
        "Mercury": eph["mercury barycenter"],
        "Venus": eph["venus barycenter"],
        "Mars": eph["mars barycenter"],
        "Jupiter": eph["jupiter barycenter"],
        "Saturn": eph["saturn barycenter"],
    }
    loc = wgs84.latlon(LAT, LON, elevation_m=ELEV_M)
    topo = earth + loc

    t_event = ts.from_datetime(datetime(2026, 11, 21, 20, 15, tzinfo=MST))
    window = [
        ts.from_datetime(datetime(2026, 11, 21, 19, 45, tzinfo=MST)),
        ts.from_datetime(datetime(2026, 11, 21, 20, 0, tzinfo=MST)),
        t_event,
        ts.from_datetime(datetime(2026, 11, 21, 20, 30, tzinfo=MST)),
        ts.from_datetime(datetime(2026, 11, 21, 20, 45, tzinfo=MST)),
    ]
    labels = ["19:45", "20:00", "20:15", "20:30", "20:45"]

    # Twilight / sunrise-sunset on 21 Nov, local
    t0 = ts.from_datetime(datetime(2026, 11, 21, 12, 0, tzinfo=MST))
    t1 = ts.from_datetime(datetime(2026, 11, 22, 2, 0, tzinfo=MST))
    f_dark = dark_twilight_day(eph, loc)
    # 0=dark, 1=astro twi, 2=nautical, 3=civil, 4=day
    times, events = find_discrete(t0, t1, f_dark)
    twilight_events = []
    names = {
        0: "night / astronomical twilight ends (sun alt < -18°)",
        1: "astronomical twilight boundary (sun alt = -18°)",
        2: "nautical twilight boundary (sun alt = -12°)",
        3: "civil twilight boundary (sun alt = -6°)",
        4: "day / sunrise-sunset boundary (sun alt = 0°)",
    }
    # Also use risings_and_settings for sun
    f_set = risings_and_settings(eph, sun, loc)
    stimes, sevents = find_discrete(t0, t1, f_set)
    sun_events = []
    for t, ev in zip(stimes, sevents):
        kind = "sunrise" if ev else "sunset"
        sun_events.append({
            "kind": kind,
            "mst": t.utc_datetime().replace(tzinfo=timezone.utc).astimezone(MST).strftime("%Y-%m-%d %H:%M:%S %Z"),
            "utc": t.utc_iso(),
        })

    # Interpret dark_twilight_day transitions more carefully by sampling sun altitude
    def sun_alt(t):
        alt, _, _ = topo.at(t).observe(sun).apparent().altaz()
        return alt.degrees

    # Find sunset as last moment sun alt crosses 0 going down, etc., by scanning
    scan = ts.utc(2026, 11, 21, 16, range(0, 20*60, 1))  # 16:00-ish UTC? wait that's wrong
    # 21 Nov 16:00 MST = 23:00 UTC Nov 21 through 02:00 UTC Nov 22 is late.
    # Sunset is late afternoon: scan 16:00-19:30 MST = 23:00 UTC Nov 21 to 02:30 UTC Nov 22
    start = datetime(2026, 11, 21, 16, 0, tzinfo=MST)
    minutes = [ts.from_datetime(start + timedelta(minutes=i)) for i in range(0, 7*60 + 1)]
    alts = [sun_alt(t) for t in minutes]
    crossings = {}
    thresholds = [(0, "sunset (sun alt 0°)"), (-6, "end of civil twilight"),
                  (-12, "end of nautical twilight"), (-18, "end of astronomical twilight")]
    for th, name in thresholds:
        for i in range(1, len(alts)):
            if alts[i-1] >= th > alts[i]:
                # linear interpolate
                frac = (alts[i-1] - th) / (alts[i-1] - alts[i]) if alts[i] != alts[i-1] else 0
                tcross = ts.tdb_jd(minutes[i-1].tdb + frac * (minutes[i].tdb - minutes[i-1].tdb))
                crossings[name] = tcross.utc_datetime().replace(tzinfo=timezone.utc).astimezone(MST).strftime("%Y-%m-%d %H:%M:%S %Z")
                break

    report = {
        "calculation_point": {
            "note": "Public Alamosa-area reference used for ephemeris only; not an exact observer coordinate.",
            "lat_deg": LAT, "lon_deg": LON, "elev_m": ELEV_M,
            "west_az_window_deg": [WEST_AZ_MIN, WEST_AZ_MAX],
        },
        "computed_at_mst": datetime.now(MST).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "event_time_mst": "2026-11-21 20:15:00 MST",
        "event_time_utc": "2026-11-22 03:15:00Z",
        "sun_twilight_mst": crossings,
        "sun_rise_set": sun_events,
        "horizon_estimate": [],
        "objects_at_times": {},
        "western_at_2015": [],
        "sidereal_and_planet_drift": {},
        "satellite_passes": {},
        "tle_epochs": [],
    }

    for name, lat, lon, h in WEST_PEAKS:
        dist, brg, elev = horizon_angle(LAT, LON, ELEV_M, lat, lon, h)
        report["horizon_estimate"].append({
            "feature": name,
            "distance_km": round(dist, 1),
            "azimuth_deg": round(brg, 1),
            "approx_geometric_elevation_deg": round(elev, 2),
            "note": "Rough geometry only (haversine + Earth curvature; no refraction). Peak coords are published summit approximations.",
        })

    def mag_of(name, body, t, app):
        if name == "Moon":
            # Approximate illuminated fraction / standard moon mag is messy; give phase
            return None, "phase used instead of a single magnitude"
        try:
            return float(planetary_magnitude(app)), None
        except Exception as e:
            return None, str(e)

    # Moon phase
    def moon_illumination(t):
        # fraction of moon facing sun as seen from earth (elongation-based)
        sun_app = earth.at(t).observe(sun).apparent()
        moon_app = earth.at(t).observe(moon).apparent()
        sep = sun_app.separation_from(moon_app).degrees
        # illuminated fraction ~ (1 + cos(phase_angle))/2; phase angle ~ 180 - elongation for rough
        # Better: use skyfield's phase angle if available
        try:
            from skyfield.almanac import moon_phase
            # moon_phase returns angle 0 new, 180 full
            ang = moon_phase(eph, t).degrees
            frac = (1 - math.cos(math.radians(ang))) / 2.0  # actually 0 new should be 0: (1-cos0)/2=0; (1-cos180)/2=1. Good if 0=new.
            return ang, frac
        except Exception:
            frac = (1 + math.cos(math.radians(180 - sep))) / 2.0
            return 180 - sep, frac

    phase_ang, illum = moon_illumination(t_event)
    report["moon_phase_at_2015"] = {
        "phase_angle_deg_0_new_180_full": round(phase_ang, 1),
        "illuminated_fraction": round(illum, 3),
    }

    # Positions at each window time
    bodies = [("Moon", moon), ("Sun", sun)] + list(planets.items())
    stars = {n: (Star(ra_hours=ra, dec_degrees=dec), mag) for n, (ra, dec, mag) in BRIGHT_STARS.items()}

    def record_for(t):
        rows = []
        # Sun
        az, alt, app = az_alt(eph, sun, topo, t)
        rows.append({"name": "Sun", "kind": "sun", "az": az, "alt": alt, "mag": None})
        az, alt, app = az_alt(eph, moon, topo, t)
        rows.append({"name": "Moon", "kind": "moon", "az": az, "alt": alt, "mag": None,
                     "illuminated_fraction": round(illum, 3) if t is t_event else None})
        for name, body in planets.items():
            az, alt, app = az_alt(eph, body, topo, t)
            mag, err = mag_of(name, body, t, app)
            rows.append({"name": name, "kind": "planet", "az": az, "alt": alt, "mag": mag})
        for name, (star, mag) in stars.items():
            app = topo.at(t).observe(star).apparent()
            alt, az, _ = app.altaz()
            rows.append({"name": name, "kind": "star", "az": az.degrees, "alt": alt.degrees, "mag": mag})
        return rows

    for lab, t in zip(labels, window):
        rows = record_for(t)
        # Keep compact: objects with alt > -5 and (west window or very bright above horizon)
        kept = []
        for r in rows:
            in_west = WEST_AZ_MIN <= r["az"] <= WEST_AZ_MAX
            up = r["alt"] > -3
            if r["name"] == "Sun" or (up and (in_west or (r["alt"] > 10 and (r["mag"] is None or r["mag"] < 1.5) and r["kind"] != "star"))):
                kept.append({k: (round(v, 2) if k in ("az", "alt", "mag") and isinstance(v, float) else v)
                             for k, v in r.items()})
            elif up and in_west:
                kept.append({k: (round(v, 2) if k in ("az", "alt", "mag") and isinstance(v, float) else v)
                             for k, v in r.items()})
        # Always include all western objects above -3 and all mag<1.5 above 0
        kept_names = {x["name"] for x in kept}
        for r in rows:
            in_west = WEST_AZ_MIN <= r["az"] <= WEST_AZ_MAX and r["alt"] > -3
            bright_up = r["alt"] > 0 and r.get("mag") is not None and r["mag"] < 1.5
            if (in_west or bright_up) and r["name"] not in kept_names:
                kept.append({k: (round(v, 2) if k in ("az", "alt", "mag") and isinstance(v, float) else v)
                             for k, v in r.items()})
                kept_names.add(r["name"])
        report["objects_at_times"][lab] = kept

    # Focused 20:15 western list (alt > -2, az 200-320), plus notable others
    rows_2015 = record_for(t_event)
    west = [r for r in rows_2015 if WEST_AZ_MIN <= r["az"] <= WEST_AZ_MAX and r["alt"] > -2]
    west.sort(key=lambda r: r["alt"], reverse=True)
    report["western_at_2015"] = [
        {k: (round(v, 2) if k in ("az", "alt", "mag") and isinstance(v, float) else v) for k, v in r.items()}
        for r in west
    ]
    report["all_bright_up_at_2015"] = [
        {k: (round(v, 2) if k in ("az", "alt", "mag") and isinstance(v, float) else v) for k, v in r.items()}
        for r in sorted(rows_2015, key=lambda r: r["alt"], reverse=True)
        if r["alt"] > 0 and (r["kind"] != "star" or (r.get("mag") is not None and r["mag"] <= 1.5))
    ]

    # Sidereal / planet drift: same clock time 20:15 MST on earlier dates
    drift_dates = [
        ("2026-08-01", datetime(2026, 8, 1, 20, 15, tzinfo=MST)),
        ("2026-08-07", datetime(2026, 8, 7, 20, 15, tzinfo=MST)),
        ("2026-10-01", datetime(2026, 10, 1, 20, 15, tzinfo=MST)),
        ("2026-10-07", datetime(2026, 10, 7, 20, 15, tzinfo=MST)),
        ("2026-11-21", datetime(2026, 11, 21, 20, 15, tzinfo=MST)),
    ]
    # Track a few western-at-Nov objects and also show sidereal rate
    sidereal_minutes_per_day = 3.0 + 56.0/60.0  # 3m 56s
    report["sidereal_rate"] = {
        "minutes_earlier_per_day": round(sidereal_minutes_per_day, 3),
        "aug1_to_nov21_days": (datetime(2026, 11, 21) - datetime(2026, 8, 1)).days,
        "aug1_to_nov21_shift_hours": round((datetime(2026, 11, 21) - datetime(2026, 8, 1)).days * sidereal_minutes_per_day / 60.0, 2),
        "oct1_to_nov21_days": (datetime(2026, 11, 21) - datetime(2026, 10, 1)).days,
        "oct1_to_nov21_shift_hours": round((datetime(2026, 11, 21) - datetime(2026, 10, 1)).days * sidereal_minutes_per_day / 60.0, 2),
        "note": "A fixed star at a given azimuth at 20:15 MST on date D appears at that same azimuth ~3m56s earlier each following day. Over months the clock time of a given star-azimuth therefore slides earlier by hours, so a star cannot remain at 20:15 from August or October through 21 November.",
    }

    track_names = ["Venus", "Mars", "Jupiter", "Saturn", "Moon", "Fomalhaut", "Altair", "Deneb", "Vega", "Antares", "Arcturus"]
    drift = {}
    for name in track_names:
        drift[name] = []
        for lab, dt in drift_dates:
            t = ts.from_datetime(dt)
            if name in planets:
                az, alt, app = az_alt(eph, planets[name], topo, t)
                mag, _ = mag_of(name, planets[name], t, app)
                kind = "planet"
            elif name == "Moon":
                az, alt, app = az_alt(eph, moon, topo, t)
                mag, kind = None, "moon"
            else:
                star, mag0 = stars[name]
                app = topo.at(t).observe(star).apparent()
                alt_a, az_a, _ = app.altaz()
                az, alt, mag, kind = az_a.degrees, alt_a.degrees, mag0, "star"
            drift[name].append({
                "date": lab, "az": round(az, 2), "alt": round(alt, 2),
                "mag": (round(mag, 2) if isinstance(mag, float) else mag),
                "in_west_window": WEST_AZ_MIN <= az <= WEST_AZ_MAX and alt > 0,
            })
    report["sidereal_and_planet_drift"] = drift

    # For a star that is in the west at 20:15 on Nov 21, when would it have been at that az in Oct/Aug?
    # Already covered by the shift hours.

    # Satellites
    visual = load_tles(DATA / "visual.txt")
    stations = load_tles(DATA / "stations.txt")
    starlink = load_tles(DATA / "starlink.txt")
    report["tle_epochs"] = [
        tle_epoch_summary(visual, "CelesTrak GROUP=visual"),
        tle_epoch_summary(stations, "CelesTrak GROUP=stations"),
        tle_epoch_summary(starlink, "CelesTrak GROUP=starlink"),
    ]
    tle_retrieved = datetime.now(MST).strftime("%Y-%m-%d %H:%M:%S %Z")
    report["tle_retrieved_mst"] = tle_retrieved
    report["tle_caveat"] = (
        "TLEs were downloaded on 22 Nov 2026 (America/Denver) and propagated backward "
        "to 21 Nov 2026 20:00–20:30 MST (~24 hours earlier than the retrieval). "
        "ISS/visual-sat errors over one day are typically a few km (small in sky angle if the pass is high), "
        "but Starlink spacecraft maneuver often, so a reconstruction from later TLEs can miss, add, or time-shift trains. "
        "This is not a substitute for epoch-matched historical TLEs."
    )

    # Sample every 15s from 20:00 to 20:30 MST
    n_samp = int(30 * 60 / 15) + 1
    dt0 = datetime(2026, 11, 21, 20, 0, tzinfo=MST)
    sample_dts = [dt0 + timedelta(seconds=15 * i) for i in range(n_samp)]
    sample_ts = ts.from_datetimes(sample_dts)

    def find_passes(sats, min_alt=10.0, require_sunlit=True, western_only=False):
        hits = []
        for sat in sats:
            try:
                rel = (sat - loc).at(sample_ts)
                alt, az, dist = rel.altaz()
                alts = alt.degrees
                azs = az.degrees
                if require_sunlit:
                    try:
                        sunlit = sat.at(sample_ts).is_sunlit(eph)
                    except Exception:
                        sunlit = [True] * len(sample_dts)
                else:
                    sunlit = [True] * len(sample_dts)
            except Exception:
                continue
            idxs = []
            for i, a in enumerate(alts):
                if a < min_alt:
                    continue
                if require_sunlit and not bool(sunlit[i]):
                    continue
                if western_only and not (WEST_AZ_MIN <= azs[i] <= WEST_AZ_MAX):
                    continue
                idxs.append(i)
            if not idxs:
                continue
            # group contiguous
            groups, cur = [], [idxs[0]]
            for i in idxs[1:]:
                if i == cur[-1] + 1:
                    cur.append(i)
                else:
                    groups.append(cur)
                    cur = [i]
            groups.append(cur)
            for g in groups:
                i_max = max(g, key=lambda i: alts[i])
                hits.append({
                    "name": sat.name.strip(),
                    "start_mst": sample_dts[g[0]].strftime("%H:%M:%S"),
                    "end_mst": sample_dts[g[-1]].strftime("%H:%M:%S"),
                    "max_alt_deg": round(float(alts[i_max]), 1),
                    "az_at_max_deg": round(float(azs[i_max]), 1),
                    "time_at_max_mst": sample_dts[i_max].strftime("%H:%M:%S"),
                    "in_west_at_max": WEST_AZ_MIN <= float(azs[i_max]) <= WEST_AZ_MAX,
                    "min_az": round(float(min(azs[i] for i in g)), 1),
                    "max_az": round(float(max(azs[i] for i in g)), 1),
                })
        hits.sort(key=lambda h: (h["start_mst"], -h["max_alt_deg"]))
        return hits

    # ISS / stations and visual first (small)
    iss_like = [s for s in stations + visual if "ISS" in s.name.upper() or "ZARYA" in s.name.upper()]
    # unique by name
    seen = set()
    iss_sats = []
    for s in iss_like:
        if s.name not in seen:
            iss_sats.append(s)
            seen.add(s.name)

    report["satellite_passes"]["iss_stations_alt_ge_10_sunlit"] = find_passes(stations, 10, True, False)
    report["satellite_passes"]["visual_alt_ge_10_sunlit_west"] = find_passes(visual, 10, True, True)
    report["satellite_passes"]["visual_alt_ge_10_sunlit_all_az"] = find_passes(visual, 10, True, False)

    # Starlink: more expensive. Filter by sampling a coarser grid first? Do full 15s — 10k sats * 121 samples is heavy but maybe OK.
    # Optimize: first check a few times.
    print("computing starlink (this may take a bit)...", flush=True)
    sl_west = find_passes(starlink, 10, True, True)
    sl_all = find_passes(starlink, 15, True, False)  # all-az, higher min alt
    report["satellite_passes"]["starlink_alt_ge_10_sunlit_west"] = sl_west
    report["satellite_passes"]["starlink_alt_ge_15_sunlit_all_az_count"] = len(sl_all)
    report["satellite_passes"]["starlink_alt_ge_15_sunlit_all_az_top"] = sl_all[:40]

    # Train detection: many starlinks with similar start times
    def cluster_trains(hits, bin_sec=60):
        if not hits:
            return []
        bins = defaultdict(list)
        for h in hits:
            hh, mm, ss = map(int, h["start_mst"].split(":"))
            key = (hh * 60 + mm)  # minute
            bins[key].append(h)
        trains = []
        for k, hs in sorted(bins.items()):
            if len(hs) >= 3:
                trains.append({
                    "minute_mst": f"{k//60:02d}:{k%60:02d}",
                    "n": len(hs),
                    "az_range": [min(h["az_at_max_deg"] for h in hs), max(h["az_at_max_deg"] for h in hs)],
                    "alt_range": [min(h["max_alt_deg"] for h in hs), max(h["max_alt_deg"] for h in hs)],
                    "names_sample": [h["name"] for h in hs[:8]],
                })
        return trains

    report["satellite_passes"]["starlink_west_trains_by_start_minute"] = cluster_trains(
        report["satellite_passes"]["starlink_alt_ge_10_sunlit_west"]
    )
    report["satellite_passes"]["starlink_allaz15_trains_by_start_minute"] = cluster_trains(sl_all)

    def _jsonable(o):
        try:
            import numpy as np
            if isinstance(o, (np.bool_,)):
                return bool(o)
            if isinstance(o, np.floating):
                return float(o)
            if isinstance(o, np.integer):
                return int(o)
        except Exception:
            pass
        if isinstance(o, bool):
            return bool(o)
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")
    out_json = OUT / "sky_context_2026-11-21.json"
    out_json.write_text(json.dumps(report, indent=2, default=_jsonable))

    print("wrote", out_json)

    # Human-readable summary to stdout
    print("\n======= TWILIGHT =======")
    for k, v in crossings.items():
        print(f"  {k}: {v}")
    print("Moon phase angle (0 new, 180 full):", report["moon_phase_at_2015"])
    print("\n======= HORIZON =======")
    for h in report["horizon_estimate"]:
        print(f"  {h['feature']}: {h['distance_km']} km, az {h['azimuth_deg']}°, elev {h['approx_geometric_elevation_deg']}°")
    print("\n======= WESTERN OBJECTS AT 20:15 MST =======")
    for r in report["western_at_2015"]:
        print(f"  {r['name']:12} {r['kind']:7} az {r['az']:6.2f}  alt {r['alt']:6.2f}  mag {r['mag']}")
    print("\n======= ALL BRIGHT ABOVE HORIZON AT 20:15 =======")
    for r in report["all_bright_up_at_2015"]:
        print(f"  {r['name']:12} {r['kind']:7} az {r['az']:6.2f}  alt {r['alt']:6.2f}  mag {r['mag']}")
    print("\n======= DRIFT 20:15 MST =======")
    for name, rows in report["sidereal_and_planet_drift"].items():
        print(name)
        for r in rows:
            flag = " WEST" if r["in_west_window"] else ""
            print(f"  {r['date']} az {r['az']:6.1f} alt {r['alt']:6.1f} mag {r['mag']}{flag}")
    print("\n======= TLE EPOCHS =======")
    for e in report["tle_epochs"]:
        print(e)
    print("\n======= ISS/STATIONS sunlit >=10° =======")
    for h in report["satellite_passes"]["iss_stations_alt_ge_10_sunlit"]:
        print(h)
    print("visual west", len(report["satellite_passes"]["visual_alt_ge_10_sunlit_west"]))
    for h in report["satellite_passes"]["visual_alt_ge_10_sunlit_west"][:20]:
        print(" ", h)
    print("visual all", len(report["satellite_passes"]["visual_alt_ge_10_sunlit_all_az"]))
    for h in report["satellite_passes"]["visual_alt_ge_10_sunlit_all_az"][:20]:
        print(" ", h)
    print("starlink west", len(sl_west), "trains", report["satellite_passes"]["starlink_west_trains_by_start_minute"])
    print("starlink allaz>=15", len(sl_all), "trains", report["satellite_passes"]["starlink_allaz15_trains_by_start_minute"])


if __name__ == "__main__":
    main()
