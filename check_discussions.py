import requests

r = requests.get(
    'https://api.github.com/repos/banghezhang-lang/animefit',
    headers={
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    },
    timeout=15
)
print('Status:', r.status_code)
if r.status_code == 200:
    data = r.json()
    print('has_discussions:', data.get('has_discussions'))
    print('default_branch:', data.get('default_branch'))
else:
    print(r.text[:300])
