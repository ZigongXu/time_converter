# Changelog

## 2026-02-22 — Bug fixes for NumPy compatibility and Chang'E 4 lunar day offset

### Problem 1: `np.float` removed in NumPy 1.20+

**File:** `time_converter/converters/msl/chronos.py`

**Symptom:** All SCLK-related conversions raised `AttributeError: module 'numpy' has no attribute 'float'`.

**Cause:** `np.float` was a deprecated alias for Python's built-in `float` and was removed in NumPy 1.20. The code in `_load_sclk_data()` used `np.float` as a dtype converter in `np.genfromtxt`.

**Fix:** Replaced all three occurrences of `np.float` with `float`.

---

### Problem 2: Chang'E 4 lunar day off-by-one and `IndexError` for `lunarday=1`

**Files:** `time_converter/converters/spice_utilities.py`, `time_converter/tests/test_time_converter.py`

**Symptom:** Using `lunarday=1` as direct input to `Time((1, ...), 'ce4lst')` raised `IndexError: SpiceCell index out of range`. As a workaround, the codebase (README, tests) instructed users to pass `lunarday+1` instead. Even with that workaround, all day numbers were off by one — `2019-03-20` was reported as day 4 instead of day 3.

**Root cause:** The Chang'E 4 landing site (`FIRST_LUNARDAY = 2018-12-22 16:25:51.6`) is located almost exactly at the solar midnight meridian. The actual solar midnight crossing detected by SPICE occurs only **6 seconds after landing** (`2018-12-22 16:25:57.9`). When `gfposc` searches for midnight crossings starting from `FIRST_LUNARDAY`, it immediately finds this near-zero-offset crossing and inserts it as `day_cache[0]`. This means:

- `day_cache[0]` = `2018-12-22 16:25:57.9` (spurious, essentially the start of the search)
- `day_cache[1]` = `2019-01-21 07:04:20.3` (actual end of day 1)

The `searchsorted` day numbering then shifted all days forward by 1. For `lunarday=1`, the search interval for a specific LST collapsed to zero length (start == end == `day_cache[0]`), causing the `IndexError`.

This bug was introduced by a newer version of `spiceypy` (≥6.0.0) which correctly detects the near-immediate crossing that older versions missed.

**Fix:** In `spice_utilities.py`, both `datetime_to_solarday_number` and `lst_to_datetime` now start the initial `gfposc` search from `startdate + 1 day` instead of `startdate` when the day cache is empty. Since a lunar day is ~29.5 Earth days, a 1-day offset safely skips any crossing that coincides with or immediately follows the landing epoch, without missing the true end-of-day-1 boundary.

**Tests updated** (`time_converter/tests/test_time_converter.py`):
- Removed the `lunarday+1` workaround throughout — `lunarday=1` now works as direct input.
- Updated `test_values`: `2019-03-20` now correctly maps to day 3 (was 4).
- Updated `test_values_reverse`: expected datetimes updated to match current `spiceypy` output.

**Verified:** `Time((day, dt.time(0, 0)), 'ce4lst').to('dt')` works correctly for all lunar days 1–70 with no errors.
