# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Install for development:**
```bash
pip install -e ".[dev,spice]"
# or without spice:
pip install -e ".[dev]"
```

**Run tests:**
```bash
pytest time_converter/tests/
```

**Run a single test:**
```bash
pytest time_converter/tests/test_time_converter.py::test_consistency
```

**Run tests with coverage:**
```bash
pytest --cov=time_converter time_converter/tests/
```

**Build distribution:**
```bash
python setup.py sdist bdist_wheel
```

**Regenerate Chang'E 4 precomputed data** (requires SPICE kernels at a local path):
```bash
python time_converter/generate_spice_files.py
```

## Architecture

The core abstraction is the `Converter` abstract base class (`time_converter/__init__.py`). Every supported time unit is implemented as a subclass of `Converter` with three methods:
- `supports(unit, datatype)` — returns True if this converter handles the given unit string or Python type
- `convert_to_datetime(value)` — converts from the unit to `datetime.datetime`
- `convert_from_datetime(datetime)` — converts from `datetime.datetime` to the unit

The `Time` class (`time_converter/__init__.py`) uses `Converter.__subclasses__()` to automatically discover all registered converters. All converters are imported before `Time` is defined, so subclass registration happens at import time.

**Converter modules:**
- `converters/earth.py` — `DatetimeConverter`, `DoyConverter`, `DecimalYearConverter`, `PosixConverter`
- `converters/msl/__init__.py` — `SolConverter` (MSL sols since landing 2012-08-05), `SclkConverter` (uses `chronos.py`)
- `converters/msl/chronos.py` — pure Python reimplementation of NASA SPICE SCLK kernel; reads `msl.tsc`
- `converters/change4/__init__.py` — `Change4LocalTimeConverter` for Chang'E 4 lunar day + local solar time (`ce4lst`)
- `converters/spice_utilities.py` — SPICE-based helper functions used by `Change4LocalTimeConverter`

**Chang'E 4 dual-mode design:** `Change4LocalTimeConverter` works in two modes:
1. With `spiceypy` installed: uses live SPICE computations (better accuracy)
2. Without `spiceypy`: falls back to a precomputed lookup table (`change4_localtime.dat`, valid through 2032)

**Known bug (ce4lst, lunar day 1):** When `lunarday == 1` is used as input to `ce4lst` conversions, `spiceypy` returns an empty result causing `IndexError`. The workaround is to pass `lunarday + 1` as input:
```python
Time((lunarday + 1, dt.time(8, 30)), 'ce4lst')
```
The test suite already applies this workaround.

**Adding a new unit:** Subclass `Converter` in any module imported by `time_converter/__init__.py` (or in one of the existing converter modules). It will be auto-discovered.
