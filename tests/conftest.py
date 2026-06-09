import os

# Demo seed is enabled by default for source runs; keep explicit flag for tests.
os.environ.setdefault("OSAH_ENABLE_DEMO_SEED", "1")
