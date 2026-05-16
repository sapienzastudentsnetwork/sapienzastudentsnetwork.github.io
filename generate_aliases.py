import os
import shutil
from pathlib import Path

# Check if aliases should be generated based on the environment variable
generate_aliases = os.environ.get('GENERATE_ALIASES', 'false').lower() == 'true'

# Define the target-to-aliases mapping dictionary
mappings = {
    "acsai": ["30786", "33502"],
    "compsci": ["29932", "33508", "computerscience"],
    "cybersec": ["29389", "33516", "cybersecurity"],
    "datasci": ["32344", "33519", "datascience"],
    "it": ["informatica", "inf", "29923", "29400", "33503", "33504"]
}

# Cleanup previous generated aliases in static/aliases/ to avoid orphaned files
for aliases in mappings.values():
    for alias in aliases:
        alias_dir = Path(f'static/aliases/{alias}')
        if alias_dir.exists():
            shutil.rmtree(alias_dir)

# Exit early if generation is disabled
if not generate_aliases:
    exit(0)

for target, aliases in mappings.items():
    target_dir = Path(f'public/{target}')

    if not target_dir.exists():
        continue

    for html_file in target_dir.glob('**/*.html'):
        rel_path = html_file.relative_to(target_dir)

        for alias in aliases:
            # Write to static/ so Hugo's live server can serve them
            dest_file = Path(f'static/aliases/{alias}') / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            if rel_path.name == 'index.html':
                if str(rel_path.parent) != '.':
                    path_suffix = f"{target}/{rel_path.parent}/"
                else:
                    path_suffix = f"{target}/"
            else:
                path_suffix = f"{target}/{rel_path}"

            path_suffix = path_suffix.replace('\\', '/')
            # Using relative root path (/) works flawlessly on localhost and production
            url_path = f"/{path_suffix}"

            hugo_alias_template = f'''<!DOCTYPE html>
<html lang="{target}">
  <head>
    <title>{url_path}</title>
    <link rel="canonical" href="{url_path}">
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0; url={url_path}">
  </head>
</html>'''

            dest_file.write_text(hugo_alias_template, encoding='utf-8')