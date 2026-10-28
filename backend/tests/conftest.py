"""Test-session isolation.

``services/execution_logger.py`` resolves its JSON log relative to the backend
checkout (it used to be a hardcoded /app path that silently failed outside the
container). Point it at a temp file before any test imports the app, so test
requests never write into the committed ``backend/execution_logs.json``.
"""

import os
import tempfile

os.environ.setdefault(
    "HIC_EXECUTION_LOG_FILE",
    os.path.join(tempfile.mkdtemp(prefix="hic-tests-"), "execution_logs.json"),
)
