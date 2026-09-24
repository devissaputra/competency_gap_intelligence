import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from competency_gap_intelligence.core import competency_gaps

required={'analytics':4,'instructional_design':4}
observed={'analytics':2,'instructional_design':3}
for gap in competency_gaps(required, observed):
    print(f"{gap['skill']}: gap={gap['gap']}, priority={gap['priority']:.1f}")
