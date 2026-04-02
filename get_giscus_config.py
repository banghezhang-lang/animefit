import requests
import base64

# Get repo's node_id (giscus uses this as repoId)
r = requests.get(
    'https://api.github.com/repos/banghezhang-lang/animefit',
    headers={
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    },
    timeout=15
)
data = r.json()
node_id = data.get('node_id', '')
# giscus repoId is base64 of the node_id without the prefix
# e.g. "REPO_xxxxxxxxxxxx" -> base64 encode
if node_id:
    encoded = base64.b64encode(node_id.encode()).decode()
    print('node_id:', node_id)
    print('giscus repoId:', encoded)
else:
    print('No node_id found')
    print('Full response:', data)
