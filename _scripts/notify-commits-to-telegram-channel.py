import requests
from datetime import datetime
import os
import json

# Get repository and branch information from environment variables
repo = os.getenv('GITHUB_REPOSITORY')
branch = os.getenv('GITHUB_REF_NAME')
commits = os.getenv('GITHUB_EVENT_COMMITS')

# Check if the branch is 'main'
if branch != 'main':
    print("Not on the main branch. No notifications will be sent.")
    exit(0)

# Convert the JSON-like string to a Python list using json.loads
commits_list = json.loads(commits)

# Hard-coded conversion table: Full Name -> GitHub Username
author_conversion_table = {
    "Lorenzo Antonelli": "Lorenzoantonelli",
    "Leonardo Biason": "ElBi21",
    "Ionut Cicio": "CuriousCI",
    "Matteo Collica": "matypist",
    "Oriana Deliallisi": "orianani311",
    "Rokshana Diya": "RoxyDiya",
    "Marcello Galisai": "marcellogalisai",
    "Michele Palma": "palmaaaa"
}

# Iterate over each commit in the push
for commit in commits_list:
    commit_sha = commit['id']
    commit_url = f'https://github.com/{repo}/commit/{commit_sha}'
    author_name = commit['author']['name']
    commit_message = commit['message']
    commit_timestamp = datetime.strptime(commit['timestamp'], '%Y-%m-%dT%H:%M:%S%z')

    # Map the author's full name to their GitHub username
    author_username = author_conversion_table.get(author_name, author_name)
    author_profile_url = f'https://github.com/{author_username}'

    # Format the commit date
    formatted_date = commit_timestamp.strftime('%Y-%m-%d %H:%M:%S')

    # Prepare the message to send
    message = (
        f'<b><u>New Commit</u></b> <a href="{commit_url}">[🌐]</a>'
        f'\n\n👤 <a href="{author_profile_url}">{author_username}</a> • <code>{formatted_date}</code>'
        f'\n\n{commit_message}'
    )

    # Send the message to Telegram
    url = f'https://api.telegram.org/bot{os.getenv("TELEGRAM_BOT_TOKEN")}/sendMessage'
    data = {
        'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
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
