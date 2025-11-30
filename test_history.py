import sys
sys.path.insert(0, '.')
from travel_assistant_improved import load_checklist_history

history = load_checklist_history()
print(f"找到 {len(history)} 条历史记录:")
for h in history:
    print(f"  - {h['destination']} ({h['duration']}) - {h['timestamp']}")
