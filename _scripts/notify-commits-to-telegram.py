import requests
from datetime import datetime
import os
import json
import re

# Get repository and branch information from environment variables
repo = os.getenv('GITHUB_REPOSITORY')
branch = os.getenv('GITHUB_REF_NAME')
commits = os.getenv('GITHUB_EVENT_COMMITS')

# Check if the branch is 'main'
if branch != 'main':
    print("Not on the main branch. No notifications will be sent.")
    exit(0)

# Get full GitHub event from the event path to access real file lists
event_path = os.getenv('GITHUB_EVENT_PATH')
with open(event_path) as f:
    event_data = json.load(f)

# Hard-coded conversion table: Full Name -> GitHub Username
author_conversion_table = {
    "Lorenzo Antonelli": "Lorenzoantonelli",
    "Simone Bianco": "Exyss",
    "Leonardo Biason": "ElBi21",
    "Ionut Cicio": "CuriousCI",
    "Matteo Collica": "matypist",
    "Oriana Deliallisi": "orianani311",
    "Rokshana Diya": "RoxyDiya",
    "Marcello Galisai": "marcellogalisai",
    "Michele Palma": "palmaaaa"
}

# Iterate over each commit in the push
for commit in event_data.get('commits', []):
    commit_sha = commit['id']
    commit_url = f'https://github.com/{repo}/commit/{commit_sha}'
    commit_message = commit['message']
    commit_timestamp = datetime.strptime(commit['timestamp'], '%Y-%m-%dT%H:%M:%S%z')

    # Map the author's full name to their GitHub username
    author_info = commit.get('author', {})
    author_username = author_info.get('username') or author_info.get('name')
    author_username = author_conversion_table.get(author_username, author_username)
    author_profile_url = f'https://github.com/{author_username}'

    # Format the commit date
    formatted_date = commit_timestamp.strftime('%Y-%m-%d %H:%M:%S')

    # Collect all files touched by the commit
    # (added, modified, or removed)
    all_files = commit.get('added', []) + commit.get('modified', []) + commit.get('removed', [])

    # Build a mapping of filename -> HTML link
    file_link_map = {
        file_path: f'<a href="https://github.com/{repo}/blob/{branch}/{file_path}">{file_path}</a>'
        for file_path in all_files
    }

    # Generate a regex that matches only real file paths in the commit message
    if file_link_map:
        escaped_paths = [re.escape(path) for path in file_link_map]
        pattern = r'\b(' + '|'.join(escaped_paths) + r')\b'

        # Replace file names in the commit message with their HTML links
        def replacer(match):
            return file_link_map.get(match.group(0), match.group(0))

        linked_commit_message = re.sub(pattern, replacer, commit_message)
    else:
        linked_commit_message = commit_message

    # Prepare the message to send
    message = (
        f'<b><u>New Commit</u></b> <a href="{commit_url}">[🌐]</a>'
        f'\n\n👤 <a href="{author_profile_url}">{author_username}</a> • <code>{formatted_date}</code>'
        f'\n\n{linked_commit_message}'
    )

    # Send the message to Telegram
    url = f'https://api.telegram.org/bot{os.getenv("TELEGRAM_BOT_TOKEN")}/sendMessage'
    data = {
        'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
        'message_thread_id': os.getenv("TELEGRAM_THREAD_ID"),
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raise an error if the request failed
        print("Message sent successfully!")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        print(f"Response content: {response.text}")
    except Exception as err:
        print(f"An error occurred: {err}")
