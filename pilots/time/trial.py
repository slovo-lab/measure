#!/usr/bin/env python3
"""A one-day trial: put the same date and time questions to several servers for AI agents.

A trial, not part of the bench. Reference answers come from the IANA time zone
database (through Python's zoneinfo with the tzdata package) and from calendar
arithmetic done here; none comes from a server. Written by Claude (AI).

Servers are expected under one directory (MEASURE_TIME_DIR): Python servers in
<dir>/<name>/bin/<name>, Node servers in <dir>/node/node_modules/.bin/<command>.
"""
import datetime as dt
import importlib.metadata
import os
import sys
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from bench.mcp_client import ServerError, StdioServer  # noqa: E402

BASE = os.environ.get("MEASURE_TIME_DIR", os.path.join(os.getcwd(), "time-envs"))
UTC = dt.timezone.utc
TODAY = dt.datetime.now(UTC).date()


def local(utc_text, zone):
    """Wall-clock text in a zone for a UTC instant, from the IANA database."""
    moment = dt.datetime.fromisoformat(utc_text).replace(tzinfo=UTC)
    return moment.astimezone(ZoneInfo(zone)).strftime("%Y-%m-%d %H:%M")


def today_at_noon(zone):
    moment = dt.datetime.combine(TODAY, dt.time(12, 0), tzinfo=UTC)
    return moment.astimezone(ZoneInfo(zone)).strftime("%H:%M")


CONVERSIONS = {  # name -> (UTC instant, zone, why it is asked)
    "new-york-winter": ("2026-01-15T12:00:00", "America/New_York", "ordinary"),
    "madrid-summer": ("2026-07-15T12:00:00", "Europe/Madrid", "ordinary"),
    "kathmandu": ("2026-06-01T00:00:00", "Asia/Kathmandu", "offset of 5 h 45 min"),
    "lord-howe": ("2026-06-01T00:00:00", "Australia/Lord_Howe", "offset of 10 h 30 min"),
    "moscow-2012": ("2012-06-01T12:00:00", "Europe/Moscow", "history: UTC+4 all year in 2011-2014"),
    "apia-2011": ("2011-12-31T00:00:00", "Pacific/Apia", "history: Samoa skipped 30 December 2011"),
    "asuncion-2025": ("2025-06-01T12:00:00", "America/Asuncion", "rule changed in 2024"),
    "almaty-2024": ("2024-06-01T00:00:00", "Asia/Almaty", "rule changed in 2024"),
    "new-york-before-change": ("2026-03-08T06:59:00", "America/New_York", "one minute before clocks go forward"),
    "new-york-after-change": ("2026-03-08T07:00:00", "America/New_York", "the minute clocks go forward"),
}
# name -> (question, accepted substrings or None when the behaviour is only recorded)
QUESTIONS = {name: ("%s UTC in %s (%s)" % (utc.replace("T", " ")[:16], zone, why),
                    [local(utc, zone)[11:]]) for name, (utc, zone, why) in CONVERSIONS.items()}
QUESTIONS.update({
    "gap": ("02:30 on 8 March 2026 in New York, a time that does not exist, to UTC", None),
    "fold": ("01:30 on 1 November 2026 in New York, a time that occurs twice, to UTC "
             "(05:30 and 06:30 are both right)", None),
    "days-2100": ("Days from 28 February to 1 March 2100 (2100 is not a leap year)",
                  [str((dt.date(2100, 3, 1) - dt.date(2100, 2, 28)).days)]),
    "february-1900": ("Days in February 1900", ["28"]),
    "weekday-2100": ("Day of the week of 1 March 2100", [dt.date(2100, 3, 1).strftime("%A")]),
    "iso-week-2021": ("ISO week of 3 January 2021", [str(dt.date(2021, 1, 3).isocalendar()[1])]),
    "iso-week-2024": ("ISO week of 30 December 2024", [str(dt.date(2024, 12, 30).isocalendar()[1])]),
    "unix-2038": ("Unix time of 2038-01-19 03:14:08 UTC (one past the 32-bit limit)",
                  [str(int(dt.datetime(2038, 1, 19, 3, 14, 8, tzinfo=UTC).timestamp()))]),
    "hours-across-change": (
        "Hours from 12:00 on 28 March to 12:00 on 29 March 2026 in Madrid (clocks go forward)",
        # Both moments are taken to UTC first: Python subtracts two times in the same
        # zone by the clock face and would say 24.
        ["%d" % ((dt.datetime(2026, 3, 29, 12, tzinfo=ZoneInfo("Europe/Madrid")).astimezone(UTC)
                  - dt.datetime(2026, 3, 28, 12, tzinfo=ZoneInfo("Europe/Madrid")).astimezone(UTC)
                  ).total_seconds() // 3600)]),
    "plus-24-hours": (
        "12:00 on 28 March 2026 in Madrid plus 24 hours, as Madrid time",
        [(dt.datetime(2026, 3, 28, 12, tzinfo=ZoneInfo("Europe/Madrid")).astimezone(UTC)
          + dt.timedelta(hours=24)).astimezone(ZoneInfo("Europe/Madrid")).strftime("%H:%M")]),
    "month-end": ("31 January 2024 plus one month (a convention: 29 February is usual)", None),
    "leap-second": ("The leap second 2016-12-31 23:59:60 UTC as input", None),
})
for zone in ("Asia/Kathmandu", "Australia/Lord_Howe", "America/Asuncion", "Asia/Almaty"):
    QUESTIONS["today-" + zone] = ("12:00 UTC today (%s) in %s" % (TODAY, zone), [today_at_noon(zone)])

NY, UT = "America/New_York", "UTC"


def conversions(make):
    table = {name: make(utc, UT, zone) for name, (utc, zone, _why) in CONVERSIONS.items()}
    table["gap"] = make("2026-03-08T02:30:00", NY, UT)
    table["fold"] = make("2026-11-01T01:30:00", NY, UT)
    return table


SERVERS = {
    "mcp-server-time": ("mcp-server-time/bin/mcp-server-time", {
        "today-" + zone: ("convert_time", {"source_timezone": UT, "time": "12:00", "target_timezone": zone}, "target")
        for zone in ("Asia/Kathmandu", "Australia/Lord_Howe", "America/Asuncion", "Asia/Almaty")}),
    "mcp-datetime": ("mcp-datetime/bin/mcp-datetime", dict(
        conversions(lambda t, a, b: ("convert_time", {"time": t, "source_timezone": a, "target_timezone": b}, "target")),
        **{"weekday-2100": ("get_datetime_info", {"datetime": "2100-03-01T00:00:00", "timezone": UT}, "day_of_week"),
           "iso-week-2021": ("get_datetime_info", {"datetime": "2021-01-03T00:00:00", "timezone": UT}, "iso_week"),
           "iso-week-2024": ("get_datetime_info", {"datetime": "2024-12-30T00:00:00", "timezone": UT}, "iso_week"),
           "unix-2038": ("get_datetime_info", {"datetime": "2038-01-19T03:14:08", "timezone": UT}, "unix_time"),
           "plus-24-hours": ("shift_datetime", {"hours": 24, "base": "2026-03-28T12:00:00", "timezone": "Europe/Madrid"}),
           "month-end": ("shift_datetime", {"months": 1, "base": "2024-01-31T00:00:00", "timezone": UT}),
           "leap-second": ("get_datetime_info", {"datetime": "2016-12-31T23:59:60", "timezone": UT})})),
    "mcp-time (npm @theo.foobar)": ("node/node_modules/.bin/mcp-time", dict(
        conversions(lambda t, a, b: ("convert_timezone", {"time": t + ("Z" if a == UT else ""), "input_timezone": a, "output_timezone": b})),
        **{"plus-24-hours": ("add_time", {"time": "2026-03-28T12:00:00+01:00", "timezone": "Europe/Madrid", "duration": "24h"}),
           "leap-second": ("convert_timezone", {"time": "2016-12-31T23:59:60Z", "output_timezone": UT})})),
    "time-mcp (npm)": ("node/node_modules/.bin/time-mcp", dict(
        conversions(lambda t, a, b: ("convert_time", {"sourceTimezone": a, "targetTimezone": b, "time": t.replace("T", " ")}, "time in " + b)),
        **{"february-1900": ("days_in_month", {"date": "1900-02-01"}),
           "iso-week-2021": ("get_week_year", {"date": "2021-01-03"}, "isoWeek"),
           "iso-week-2024": ("get_week_year", {"date": "2024-12-30"}, "isoWeek"),
           "unix-2038": ("get_timestamp", {"time": "2038-01-19 03:14:08"}),
           "leap-second": ("get_timestamp", {"time": "2016-12-31 23:59:60"})})),
    "mcptimeserver (npm @brainycalc)": ("node/node_modules/.bin/mcptimeserver", dict(
        conversions(lambda t, a, b: ("convert_timezone", {"date": t + ("Z" if a == UT else ""), "fromTimezone": a, "toTimezone": b})),
        **{"days-2100": ("date_diff", {"date1": "2100-03-01", "date2": "2100-02-28", "unit": "day"}),
           "february-1900": ("days_in_month", {"date": "1900-02-01"}),
           "weekday-2100": ("day_of_week", {"date": "2100-03-01"}, "dayName"),
           "iso-week-2021": ("date_part", {"date": "2021-01-03", "part": "isoWeek"}),
           "iso-week-2024": ("date_part", {"date": "2024-12-30", "part": "isoWeek"}),
           "unix-2038": ("unix_convert", {"date": "2038-01-19T03:14:08Z"}),
           "month-end": ("adjust_time", {"date": "2024-01-31", "amount": 1, "unit": "month"}),
           "leap-second": ("unix_convert", {"date": "2016-12-31T23:59:60Z"})})),
    "mcp-simple-timeserver": ("mcp-simple-timeserver/bin/mcp-simple-timeserver", {
        "days-2100": ("calculate_time_distance", {"from_date": "2100-02-28", "to_date": "2100-03-01", "unit": "days"}, "Distance"),
        "hours-across-change": ("calculate_time_distance", {
            "from_date": "2026-03-28T12:00:00", "to_date": "2026-03-29T12:00:00",
            "unit": "hours", "timezone": "Europe/Madrid"}, "Distance")}),
}


def versions():
    out = []
    for name in ("tzdata",):
        try:
            out.append("%s %s" % (name, importlib.metadata.version(name)))
        except importlib.metadata.PackageNotFoundError:
            pass
    return ", ".join(out)


def judge(name, spec, is_error, text):
    accepted = QUESTIONS[name][1]
    flat = " ".join(text.split())
    if len(spec) > 2 and spec[2] in flat:      # look only after the key that holds the answer
        flat = flat[flat.index(spec[2]):]
    shown = flat[:110]
    if accepted is None:
        return ("refused" if is_error else "answered"), shown
    if is_error:
        return "error", shown
    return ("agrees" if any(a in flat[:120] for a in accepted) else "DIFFERS (reference %s)" % " or ".join(accepted)), shown


def main():
    print("Reference data: %s. Run on %s." % (versions(), TODAY))
    print()
    print("| Server | Question | Result | What the server said |")
    print("|---|---|---|---|")
    for server, (path, questions) in SERVERS.items():
        command = os.path.basename(path)
        os.environ["MEASURE_SERVER_" + command.upper().replace("-", "_")] = os.path.join(BASE, path)
        try:
            with StdioServer(command) as running:
                for name, spec in questions.items():
                    try:
                        is_error, _payload, text = running.call(spec[0], spec[1])
                        verdict, shown = judge(name, spec, is_error, text)
                    except Exception as exc:
                        verdict, shown = "error", "%s: %s" % (type(exc).__name__, str(exc)[:80])
                    print("| %s | %s | %s | %s |" % (server, name, verdict, shown.replace("|", "/")))
        except ServerError as exc:
            print("| %s | (start) | did not start | %s |" % (server, str(exc)[:100]))
    print()
    print("Questions:")
    for name, (words, accepted) in QUESTIONS.items():
        print("- `%s`: %s. Reference: %s" % (name, words, " or ".join(accepted) if accepted else "none; behaviour recorded"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
