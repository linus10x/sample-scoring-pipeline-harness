# Verification record

Verified October 2-3, 2026 America/Chicago, Linux. Synthetic reference scope only. This record is implementation verification.

| Command | Outcome |
|---|---|
| `python3 harness.py --report REPORT.md` | Exit 0; 22/22 blocking checks, advisory passes |
| `python3 -m unittest discover -s tests -v` | Exit 0; 12 tests |

Independent changing-follower oracles block a dropped-growth-term mutant. Earliest/latest calendar boundaries are exercised. Hosted CI and real-client scoring accuracy remain unverified.

Re-run October 3, 2026 (CT) on Python 3.10.22, 3.11.17, 3.12.14 and 3.13.5: 22/22 blocking checks and 12 tests OK on each. REPORT.md is the Python 3.12.14 run. Source targets Python 3.10+.

## Source identity before this record

SHA-256 binds this record to the source. Changes require rechecking affected assertions.

| File | SHA-256 |
|---|---|
| `.github/workflows/verify.yml` | `927e7f43a269984f7e99a5aeca216de6a2de90c5245022f22f5da703a5a5c917` |
| `.gitignore` | `862263fa1f46c20f0d1e4dac5ffcc75abd55c08211b2c3864c5f8764b9d87793` |
| `LICENSE` | `037df8cb655d4ff33487e5052e79b617699db575004c68f7e122187b8de7d67f` |
| `README.md` | `d4d1c66c610469908f8176ead11da24561448ec3e0d58d6da9cf01635f4b167d` |
| `REPORT.md` | `6508b8fb418577773781c12b7e6df52336558f06fcfb48ff1350efe6b38083ed` |
| `harness.py` | `2069f0453c599bb2d49688821a93cd17d42946e0029df0df463d8cef1cc23381` |
| `momentum/__init__.py` | `96e632ad659b11edeceba7395dd987e3a9110ed4f683fdb57daa7dcbdfc985f6` |
| `momentum/contract.py` | `e4d391c92e0fd5a11e3814c2cc8f1362efd01314438096e9eb3ba053859c09ff` |
| `momentum/generate.py` | `c8c3ebe5dbc42153e310968951e8eac91f1445bbd3aafed913843fa60d2b7313` |
| `momentum/score.py` | `d5811fa7022c4f5835cd5bd459a2587f501f1f9a808f314afeec61ee90f357e0` |
| `tests/__init__.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `tests/test_harness.py` | `239d654ebcaaa080edea3472ee7933e448723ef74af7e9799cd931b5f2c13329` |
