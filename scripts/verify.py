import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mrna_evidence.verify import verify

result = verify()
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["ok"] else 1)
