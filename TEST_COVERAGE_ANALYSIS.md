# Test Coverage Analysis

## Executive Summary

The codebase contains four source modules (`calculator`, `string_utils`,
`data_processor`, `user_account`). Three of them have partial test files;
one (`data_processor`) has **no tests at all**. Running `pytest --cov` reveals
an estimated line coverage of **~35–40%** and branch coverage well below 50%.
The 80% coverage threshold configured in `setup.cfg` would currently fail.

---

## Module-by-Module Breakdown

### 1. `src/calculator.py` — Estimated coverage: ~55%

| Function | Lines covered | Critical gaps |
|---|---|---|
| `add` | Yes | — |
| `subtract` | Yes | — |
| `multiply` | Partial | multiply-by-zero, negative × negative |
| `divide` | Partial | **zero-division `ValueError` branch never hit** |
| `power` | Partial | `TypeError` for float exponent not tested; negative exponents not tested; `x**0 == 1` not tested |
| `factorial` | Partial | **error paths (`n < 0`, `n` not int) never hit**; large values (e.g. 20!) not tested |
| `is_prime` | Partial | **`n = 0`, `n = 1`, `n = 2`, negative `n` never tested** |

**Priority fixes:**
- Add `pytest.raises` tests for every `ValueError`/`TypeError` guard.
- Cover `is_prime` edge cases (`0, 1, 2, even numbers, primes > 100`).
- Test `divide` with a floating-point result to ensure float return type.

---

### 2. `src/string_utils.py` — Estimated coverage: ~45%

| Function | Lines covered | Critical gaps |
|---|---|---|
| `truncate` | Partial | `TypeError` (non-string input), `ValueError` (zero/negative max_length), custom suffix, exact-boundary length |
| `slugify` | Partial | Unicode input, empty string, strings with only special chars |
| `count_words` | Yes | Multiple consecutive spaces; `None` input |
| `is_palindrome` | **0%** | **Completely untested** |
| `mask_sensitive` | Partial | `visible_chars >= len(text)` edge case; custom mask character |
| `camel_to_snake` | **0%** | **Completely untested** |

**Priority fixes:**
- Write a full `TestIsPalindrome` class covering: true palindrome, false, with
  punctuation/spaces (`"A man, a plan, a canal: Panama"`), empty string.
- Write a full `TestCamelToSnake` class covering: simple camelCase, PascalCase,
  consecutive uppercase letters (acronyms like `"HTTPSResponse"`), already-snake
  input.
- Add `pytest.raises` for `truncate` guard conditions.

---

### 3. `src/data_processor.py` — Estimated coverage: **0%**

This entire module is **completely untested**. It contains eight functions:

| Function | Risk level | Notes |
|---|---|---|
| `normalize` | Medium | Edge cases: empty list, all-same-value list (division-by-zero guard) |
| `chunk` | Medium | Edge case: `size <= 0` raises `ValueError`; list length not divisible by size |
| `flatten` | High | Deeply nested lists; mixed-type lists; empty lists at any level |
| `deduplicate` | Medium | Preserves insertion order; unhashable types (dicts) would raise `TypeError` |
| `summarize` | High | Empty list → empty dict; single-element list (no stdev); float precision |
| `group_by` | Medium | Key absent from some items (`None` key); empty input list |
| `filter_by` | Low | No matches → empty list; key absent in items |

**Priority fixes:** Create `tests/test_data_processor.py` from scratch. Focus
first on `normalize` (the all-same-value path is a latent zero-division guard),
`flatten` (recursive logic is hardest to reason about), and `summarize` (the
`stdev` branch only fires for `len > 1`).

---

### 4. `src/user_account.py` — Estimated coverage: ~30%

| Area | Lines covered | Critical gaps |
|---|---|---|
| `UserAccount.__post_init__` validation | Partial | Invalid username (too short, bad chars) never raises; invalid email never raises |
| `set_password` | Yes | Short-password `ValueError` not tested |
| `check_password` | Partial | **Wrong password (returns `False`) never tested** |
| Role management (`add_role`, `remove_role`, `has_role`) | **0%** | **Completely untested** |
| `activate` / `deactivate` | **0%** | **Completely untested** |
| `find_user` | Partial | Not-found path (returns `None`) never tested |

**Priority fixes:**
- Test all `ValueError` paths in `__post_init__` — these guard public API
  boundaries and should be high-confidence.
- Add a `TestRoleManagement` class covering: add a role, add a duplicate (no-op),
  remove an existing role, remove a role that was never added (no-op),
  `has_role` true/false.
- Test `check_password` with a wrong password.
- Test `activate` / `deactivate` state transitions.

---

## Recommended Improvements (Prioritised)

### P1 — Immediate (unblock the 80% coverage threshold)

1. **Create `tests/test_data_processor.py`** — this single file will bring the
   overall coverage up by ~15 percentage points. Start with happy-path tests for
   all eight functions, then add edge cases.

2. **Add error-path tests to `test_calculator.py`** — `divide(x, 0)`,
   `power(x, 1.5)`, `factorial(-1)`, `factorial(1.5)` should each have a
   `pytest.raises` assertion.

3. **Fill in `is_palindrome` and `camel_to_snake` in `test_string_utils.py`** —
   both functions have 0% coverage today.

### P2 — Short-term (raise quality floor)

4. **Test `UserAccount` validation error paths** — username and email validators
   are the public contract; any regression here would be silent without tests.

5. **Test role management and account activation** — `add_role`, `remove_role`,
   `has_role`, `activate`, `deactivate` represent ~40% of `UserAccount`'s code
   and are completely uncovered.

6. **Add boundary tests for `truncate` and `mask_sensitive`** — off-by-one bugs
   in string manipulation are common and cheap to catch with explicit boundary tests.

### P3 — Good practice (improve branch coverage)

7. **Parametrize repetitive tests** — use `@pytest.mark.parametrize` for
   `is_prime`, `is_palindrome`, and `factorial` instead of one assertion per test
   function. This makes it easy to add new cases without new test functions.

8. **Test `summarize` with a single-element list** — the `stdev` branch is only
   reachable when `len(values) > 1`; a one-element list exercises the else path
   and would otherwise be a hidden branch miss.

9. **Add integration-style tests** that chain utilities together (e.g.
   `slugify(camel_to_snake(...))`) to catch regressions at module boundaries.

---

## How to Run Coverage Locally

```bash
pip install -r requirements-dev.txt
pytest --cov=src --cov-report=term-missing --cov-branch
```

To generate an HTML report:

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

The `fail_under = 80` threshold in `setup.cfg` will cause `pytest-cov` to
return a non-zero exit code if overall coverage drops below 80%, making it
suitable as a CI gate.
