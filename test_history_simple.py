import json
import os

def test_history():
    history = []
    save_dir = "checklist_data"

    print(f"检查目录: {save_dir}")
    print(f"目录存在: {os.path.exists(save_dir)}")

    if not os.path.exists(save_dir):
        return []

    for filename in os.listdir(save_dir):
        print(f"处理文件: {filename}")
        if filename.endswith(".json"):
            file_path = os.path.join(save_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    record = {
                        "id": data.get("id", ""),
                        "destination": data.get("destination", ""),
                        "duration": data.get("duration", ""),
                        "timestamp": data.get("timestamp", ""),
                        "filename": filename
                    }
                    history.append(record)
                    print(f"  成功加载: {record['destination']} - {record['timestamp']}")
            except Exception as e:
                print(f"  加载失败: {e}")

    print(f"\n总共加载 {len(history)} 条记录")
    return history

if __name__ == "__main__":
    history = test_history()
    for h in history[:5]:
        print(f"{h['destination']} ({h['duration']}) - {h['timestamp']}")
