import os
import json
import shutil

class CollectionManager:
    def __init__(self, root_path):
        self.root_path = root_path
        if not os.path.exists(self.root_path):
            try:
                os.makedirs(self.root_path)
            except OSError:
                pass

    def get_tree(self):
        """Returns a nested dictionary representing the file structure."""
        if not os.path.exists(self.root_path):
            return {}
            
        def build_tree(path):
            tree = {'files': [], 'dirs': {}}
            try:
                items = sorted(os.listdir(path))
            except OSError:
                return tree

            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    tree['dirs'][item] = build_tree(full_path)
                elif item.endswith('.json'):
                    tree['files'].append({
                        'name': item[:-5],
                        'path': full_path
                    })
            return tree
            
        return build_tree(self.root_path)

    def create_collection(self, name, parent_path=None):
        """Creates a new folder (collection)."""
        if parent_path is None:
            parent_path = self.root_path
        
        # Sanitize name
        safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()
        if not safe_name:
            raise ValueError("Invalid collection name")
            
        path = os.path.join(parent_path, safe_name)
        if os.path.exists(path):
            raise FileExistsError("Collection already exists")
            
        os.makedirs(path)
        return path

    def save_request(self, name, data, parent_path=None):
        """Saves a request to a JSON file."""
        if parent_path is None:
            parent_path = self.root_path
            
        # Ensure name is safe
        safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).strip()
        if not safe_name:
            safe_name = "untitled"
            
        path = os.path.join(parent_path, safe_name + ".json")
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        return path
            
    def load_request(self, path):
        with open(path, 'r') as f:
            return json.load(f)

