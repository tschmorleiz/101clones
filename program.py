import requests
import json
import difflib
import os
import sys
import pipes

f_name = 'getMatch{}'.format(sys.argv[1][0].upper() + sys.argv[1][1:])

r = requests.get('http://101companies.org/endpoint/Language:Python/json/directions').text

data = json.loads(r)

data = filter(lambda c: c['predicate'] == 'http://101companies.org/property/uses', data)
data = map(lambda c: c['node'].replace('Contribution:', ''), data)

def getFiles(u):
    url = 'http://data.101companies.org/resources/contributions/{}/index.json'.format(u)

    r = requests.get(url)

    index = json.loads(r.text)
    dirs = index['dirs']
    files = index['files']

    files = map(lambda f: u + '/' + f, files)

    for d in dirs:
        files.extend(getFiles(u + '/' + d))

    return files

def downloadFile(f):
    url = 'http://worker.101companies.org/101repo/101repo/contributions/' + f
    return requests.get(url).content

result = []

i = 0
cs = {}
csFlat = {}
for c in data:
    cs[c] = {}
    for f in getFiles(c):
        if f.endswith('.py'):
            content = downloadFile(f)
            if content != '':
                cs[c][f] = content
                csFlat[f] = content
                i += len(cs[c][f])

def getMatchDiff(text1, text2):
    return difflib.SequenceMatcher(None, text1, text2).ratio()

def getMatchFragment(text1, text2):
    print 'python PyFactExtractor/extractor.py "{}" > extract1.json'.format(pipes.quote(text1))
    os.system('python PyFactExtractor/extractor.py "{}" > extract1.json'.format(pipes.quote(text1)))
    os.system('python PyFactExtractor/extractor.py "{}" > extract2.json'.format(pipes.quote(text2)))

    t1 = open('extract1.json').read()
    t2 = open('extract2.json').read()
    
    result = []
    
    for fragment in t1['fragments']:
        found = False
        for f2 in ts2['fragments']:
            if fragment['classifier'] == f2['classifier'] and fragment['name'] == f2['name']:
                found = True
                
        result.append(found)
   
    return len(filter(bool, result)) / float(len(result))

def getMatchCluster(cluster, text2):
    f = eval(f_name)

    return min(map(lambda member: f(csFlat[member], text2), cluster))

i = 0
clusters = {}

iterations = 0.0
for c in data:
    i += 1
    for f in cs[c]:
        clusters[f] = {'files': [f]}
        for cluster in clusters:
            if f == cluster:
                continue
            mindiffratio = getMatchCluster(clusters[cluster]['files'] + [cluster], cs[c][f])
            if mindiffratio >= 0.25:
                clusters[cluster]['files'].append(f)
                #if mindiffratio < clusters[cluster].get('mindiffratio', 1):
                #    clusters[cluster]['mindiffratio'] = mindiffratio


for c in clusters.keys():
    if len(clusters[c]['files']) == 1:
        del clusters[c]

for c in clusters.keys():
    origin = None
    for f in clusters[c]['files']:
        url = 'http://101companies.org/resources/contributions/{}'.format(f)
        github = json.loads(requests.get(url).text)['github']
        github = github.split('/')
        #github = github.replace('http://', 'https://')
        #github = github.replace('/tree/master', '')        
        #github = github.replace('github.com', 'api.github.com/repos')
        url = 'https://api.github.com/repos/{user}/{repo}/commits?path={path}'.format(user=github[3], repo=github[4], path='/'.join(github[7:]))
        info = json.loads(requests.get(url).text)
        info = map(lambda c: c['commit']['author'], info)
        first = sorted(info, key=lambda i: i['date'])[0]
        if not origin or origin['commit']['date'] > first['date']:
            origin = {
                'file': f,
                'commit': first
            }
    clusters[c]['origin'] = origin

print json.dumps(clusters)
