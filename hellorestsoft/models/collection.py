import os
import json

class CollectionManager:
    def __init__(self, root_path):
        self.root_path = root_path
        if not os.path.exists(self.root_path):
            try:
                os.makedirs(self.root_path)
            except OSError:
                pass

    def get_requests(self):
        items = []
        if not os.path.exists(self.root_path):
            return items
            
        for root, dirs, files in os.walk(self.root_path):
            for f in files:
                if f.endswith('.json'):
                    rel_path = os.path.relpath(os.path.join(root, f), self.root_path)
                    items.append({
                        'name': f[:-5], # remove .json
                        'path': os.path.join(root, f),
                        'rel_path': rel_path
                    })
        return sorted(items, key=lambda x: x['name'])

    def save_request(self, name, data):
        # Ensure name is safe
        safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()
        if not safe_name:
            safe_name = "untitled"
            
        path = os.path.join(self.root_path, safe_name + ".json")
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        return path
            
    def load_request(self, path):
        with open(path, 'r') as f:
            return json.load(f)
