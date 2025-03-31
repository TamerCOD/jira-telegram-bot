import os
import requests
import json

JIRA_USER = os.getenv('JIRA_USER')
JIRA_PASS = os.getenv('JIRA_PASS')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# JQL и URL запроса
jql = 'project=MS AND status=Open AND "Группа"="Контакт-Центр"'
url = f'https://jirasd.saima.kg/rest/api/2/search?jql={requests.utils.quote(jql)}&maxResults=5'

headers = {
    "Accept": "application/json"
}

# Храним уже отправленные ключи
sent_file = "sent_issues.json"
if os.path.exists(sent_file):
    with open(sent_file, "r") as f:
        sent = set(json.load(f))
else:
    sent = set()

# Получаем задачи из JIRA
response = requests.get(url, headers=headers, auth=(JIRA_USER, JIRA_PASS), verify=False)
issues = response.json().get("issues", [])

for issue in issues:
    key = issue["key"]
    summary = issue["fields"].get("summary", "Без описания")
    link = f"https://jirasd.saima.kg/browse/{key}"

    if key not in sent:
        msg = f"🆕 *{key}*\n{summary}\n{link}"
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        )
        sent.add(key)

# Обновляем список
with open(sent_file, "w") as f:
    json.dump(list(sent), f)
