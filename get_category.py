import requests

r = requests.get(
    'https://api.github.com/repos/banghezhang-lang/animefit/discussions/categories',
    headers={
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    },
    timeout=15
)
print('Status:', r.status_code)
if r.status_code == 200:
    cats = r.json()
    for c in cats:
        print('  id=%s name=%s slug=%s' % (c['id'], c['name'], c['slug']))
else:
    print(r.text[:300])
