"""Reproduce the labeled worked example; this is not an empirical study."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from competency_gap_intelligence import core
outputs={'weighted level: levels 2,4; weights 1,3': (2*1+4*3)/(1+3), 'gap: target 4 minus level 3.5': 4-3.5, 'priority: gap .5 times importance 2': .5*2}
result={'kind':'illustrative_calculation','note':'Illustrative confidence-weighted arithmetic on supplied levels.','outputs':outputs}
(ROOT/'results/review_examples.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
