from flask import Flask, render_template, send_file
import requests
import csv

GITHUB_API = 'https://api.github.com'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', result=get_issues_deployed())

@app.route('/download/csv')
def download_csv():
    result = get_issues_deployed()
    with open('issues_deployed_and_scored.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"')
        # fieldnames = ['Title', 'User', 'Labels', 'Score']
        # writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writerow(['Issues Deployed'])
        writer.writerow(['Title', 'User', 'Labels', 'Score'])
        for issue in result['issues_deployed']:
            writer.writerow([issue['title'], issue['user'], issue['labels'], issue['score']])
        writer.writerow('')
        writer.writerow(['Users Score'])
        writer.writerow(['User', 'Total Score'])
        for user in result['user_score']:
            writer.writerow([user['user'], user['score']])

    return send_file('issues_deployed_and_scored.csv')

def get_issues_deployed():
    issues_deployed = []
    request = requests.get(
        GITHUB_API + '/repos/spiraleye/singularity/issues')
    issues = request.json()
    users = []
    for issue in issues:
        labels = issue['labels']
        for label in labels:
            if label['name'][:2] == 'W:':
                scoring_label = label['name']
            if label['name'] == 'Deployed':
                for slabel in labels:
                    if slabel['name'][:2] == 'W:':
                        scoring_label = slabel['name']
                issues_deployed.append({
                    'title': issue['title'],
                    'user': issue['assignee']['login'],
                    'labels': [lab['name'] for lab in labels],
                    'score': get_score(scoring_label)
                })

    for issue in issues_deployed:
        if issue['user'] not in users:
            users.append(issue['user'])
    score_users = []
    for user in users:
        score = 0
        for issue in issues_deployed:
            score = score + issue['score']
        score_users.append({
            'user': user,
            'score': score
        })

    result = {
        'issues_deployed': issues_deployed,
        'user_score': score_users
    }

    return result


def get_score(weight):
    switch = {
        "W:1": 1,
        "W:2": 2,
        "W:3": 3,
        "W:5": 5,
        "W:8": 8
    }
    return switch.get(weight, "Invalid weight")


if __name__ == '__main__':
    app.run(port=5000)