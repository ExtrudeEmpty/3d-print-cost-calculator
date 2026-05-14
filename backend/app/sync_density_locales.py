import os
import json

base_dir = 'static/locales'
additional_dir = os.path.join(base_dir, 'additional')

# Load the base translations to get the key
with open(os.path.join(base_dir, 'en.json'), 'r') as f:
    en_data = json.load(f)
    default_val = en_data.get('default_density', 'Default Density')

# Update all files in additional
for filename in os.listdir(additional_dir):
    if filename.endswith('.json'):
        path = os.path.join(additional_dir, filename)
        with open(path, 'r') as f:
            data = json.load(f)
        
        if 'default_density' not in data:
            data['default_density'] = default_val
            with open(path, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Updated {filename}")
