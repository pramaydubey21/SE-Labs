# Lab 5: Issues Found and Fixed

**Name:** Pramay Dubey  
**SRN:** PES2UG24CS361  

**File:** `warehouse_stock_manager.py`
**Tools:** Pylint 4.1.3, Flake8 7.3.0, Bandit 1.9.4

| Tool | Before | After |
|---|---|---|
| Pylint | 37 messages, **4.48/10** | 0 messages, **10.00/10** |
| Flake8 | 19 violations | 0 |
| Bandit | 5 issues (1 High, 2 Medium, 2 Low) | No issues identified |

Original reports are in `reports_before_fix/`; the reports in the repo root are from the fixed file. Line numbers below refer to the **original** file. All issues listed were fixed.

## Issue table (high and medium severity first)

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| `eval()` on supervisor formula (Bandit B307, Pylint W0123) | Security (Medium; code injection) | 62 | `formula` comes from the supervisor console and is passed straight to `eval`. Any Python code typed there runs, e.g. `__import__('os').system(...)`. Passing `{"current": current}` as globals does not sandbox it, since builtins are still reachable. | Replaced with `evaluate_formula()`, which parses with `ast` and only allows the name `current`, whole-number literals and `+ - * //`. Anything else raises `ValueError` and the adjustment is rejected and logged. A negative result is also rejected. |
| Weak MD5 hash (Bandit B324) | Security (High) | 31 | `hashlib.md5` is flagged as broken for security use. | Checked the purpose first: it is only a 6-character bin-label checksum, not a security control. Switching to SHA-256 would change every label already printed. Kept MD5 with `usedforsecurity=False`, which states the intent and clears B324. Labels are unchanged (`WID-002` is still `a616ce`). |
| Hard-coded supervisor password (Bandit B105) | Security (Low) | 10, 59, 76 | The password `wh-admin-1234` is in the source and in Git history, so anyone with the code can adjust stock. It is also compared with `!=`, which isn't constant-time. | Password is read from the `WH_SUPERVISOR_PASSWORD` environment variable. If it is not set, adjustments are disabled. Comparison uses `hmac.compare_digest`. (The old password should be changed, since it remains in Git history.) |
| Over-issuing wipes out the SKU (runtime bug) | Bug (High) | 18–22, 73 | `removeStock("WID-001", 500)` with only 28 on hand made stock −472, so the SKU was **deleted** without any message. WID-001 disappeared from the report. | `remove_stock` rejects requests larger than the stock on hand and logs a warning. WID-001 now correctly shows 28 units. |
| Negative quantities accepted (runtime bug) | Bug (High) | 12–15, 69, 74 | `addStock("WID-002", -4)` created a SKU with **−4** units; the program printed `WID-002 stock: -4` and listed it for reorder. | `add_stock`/`remove_stock` accept only positive whole numbers (and reject `bool`). Invalid input is logged and the function returns `False`. |
| Non-string SKU accepted (runtime bug) | Bug (Medium) | 13, 70 | `addStock(404, 15)` stored an `int` key. After `saveStock`/`loadStock`, JSON turned it into the string `"404"`, so the data silently changed type. | SKUs must be non-empty strings; `404` is rejected with a warning. |
| Bare `except:` with `pass` (Pylint W0702, Flake8 E722, Bandit B110) | Bug (Medium) | 23–24 | Catches everything (even `KeyboardInterrupt`) and hides it, so issuing an unknown SKU (`GHOST-9`) silently does nothing. | Catch only `KeyError`, log a warning and return `False`. |
| Mutable default argument (Pylint W0102) | Bug (Medium) | 12 | `history=[]` is created once and shared by every call, so history entries leak between calls. | `history=None` and a new list is created inside the function. |
| Files opened without `with` (Pylint R1732) | Bug (Medium) | 34, 40, 63 | If a read or write fails, the file handle (including the audit log) is never closed. | All three use `with open(...)`. `load_stock` also handles `FileNotFoundError` and `JSONDecodeError`. |
| `eval()` used to print (Bandit B307, Pylint W0123) | Security (Medium) | 80 | `eval("print(...)")` is a needless dangerous pattern. | Replaced with a plain `print`. |
| `getStock` crashes on unknown SKU | Bug (Low) | 27, 74 | `warehouse_stock[sku]` raises `KeyError` for a SKU that is not stocked. | `get_stock` returns `warehouse_stock.get(sku, 0)`. |
| No encoding on `open()` (Pylint W1514) | Portability (Low) | 34, 40, 63 | Encoding depends on the OS locale. | `encoding="utf-8"` on every `open`. |
| `global` statement (Pylint W0603) | Design (Low) | 35 | Rebinding the global makes data flow harder to follow. | `load_stock` updates the existing dict with `clear()` + `update()`. |
| Unused variable `total_units` (Pylint W0612, Flake8 F841) | Dead code (Low) | 54 | Computed and never used. | Removed; `check_reorder` is now a list comprehension. |
| Unused imports `logging`, `os` (Pylint W0611, Flake8 F401) | Style (Low) | 2, 4 | Imported but unused. | Logging is configured in `main()` and used for every event; `os` is used to read the password env var. |
| Audit log is incomplete | Design (Low) | 64 | The audit line recorded the formula but not the old or new value. | Audit now records `from <old> to <new>` plus the formula and timestamp. |
| `%` formatting and string concatenation (Pylint C0209) | Style (Low) | 16, 47, 64 | Harder to read than f-strings. | Converted to f-strings (lazy `%s` kept in `logger` calls, as Pylint recommends). |
| Non-snake_case function names (Pylint C0103 ×9) | Style (Low) | 12–67 | `addStock`, `removeStock`, etc. break PEP 8 naming. | Renamed to `add_stock`, `remove_stock`, `get_stock`, `sku_checksum`, `load_stock`, `save_stock`, `print_report`, `check_reorder`, `apply_adjustment`. |
| Missing docstrings (Pylint C0114, C0116 ×10) | Style (Low) | 1, 12–67 | No module or function documentation. | Added a module docstring and a docstring for every function. |
| PEP 8 layout (Flake8 E302 ×10, E305, E501 ×3, W291; Pylint C0301, C0303) | Style (Low) | 12–82 | Missing blank lines, lines over 79 characters, trailing whitespace. | Two blank lines between functions; long lines split; whitespace removed. |
| Code runs on import | Design (Low) | 82 | `main()` ran whenever the module was imported. | Added `if __name__ == "__main__":` guard. |

## Program output: before vs after

**Before** (the output looked wrong in several places):
```
WID-002 stock: -4            <- negative stock
Needs reorder: ['WID-002']
Warehouse Stock Report
WID-002 -> 21 units  [chk: a616ce]
404 -> 15 units  [chk: 4f4adc]   <- int SKU accepted, now a string
stock audit complete             <- WID-001 (28 units) has vanished
```

**After** (`WH_SUPERVISOR_PASSWORD=wh-admin-1234 python warehouse_stock_manager.py`):
```
INFO: Received 40 units of WID-001
WARNING: Rejected receipt for WID-002: invalid quantity -4
WARNING: Rejected receipt: invalid SKU 404
INFO: Issued 12 units of WID-001
WARNING: Rejected issue: SKU GHOST-9 not in stock
WARNING: Rejected issue of 500 units of WID-001: only 28 on hand
WID-002 stock: 0
Needs reorder: []
INFO: Adjusted WID-002 from 0 to 25
WARNING: Rejected adjustment of WID-002: formula may only use 'current', whole numbers and + - * //
Warehouse Stock Report
WID-001 -> 28 units  [chk: c53e41]
WID-002 -> 25 units  [chk: a616ce]
stock audit complete
```
The second adjustment in the demo deliberately tries a code-injection formula (`__import__('os').getcwd()`) to show it is now rejected. If `WH_SUPERVISOR_PASSWORD` isn't set, both adjustments log `Adjustments disabled` and the rest of the demo runs normally.
