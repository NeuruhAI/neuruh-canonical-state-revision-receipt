# Changelog

## 0.1.2a0 — v0.1.2-alpha

- `LICENSE` now carries the complete Apache-2.0 license text. Earlier tags shipped only the
  short boilerplate notice, which is not the license text and is not recognised as Apache-2.0.
  A `NOTICE` file carries the copyright line that notice had held.
- Modern packaging metadata: PEP 639 `license`/`license-files`, `readme`, authors, project URLs.
- Explicit `__all__`, so `import *` no longer re-exports standard-library names, and
  `__version__` is read from installed distribution metadata.
- Continuous integration on Python 3.11, 3.12, and 3.13.
- No behavioral change.
