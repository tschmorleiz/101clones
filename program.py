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

def getMatchDiff(text2, text1):
    return difflib.SequenceMatcher(None, text1, text2).ratio()

def getMatchFragment(text1, text2):

    f = open('input1.py', 'w')
    f.write(text1)
    f.close()

    f = open('input2.py', 'w')
    f.write(text2)
    f.close()

    os.system('python PyFactExtractor/extractor.py < input1.py > extract1.json')
    os.system('python PyFactExtractor/extractor.py < input2.py > extract2.json')

    t1 = json.load(open('extract1.json'))
    t2 = json.load(open('extract2.json'))

    for fragment in t1['fragments']:
        f = open('input.py', 'w')
        f.write(text1)
        f.close()
        os.system('python PyFragmentLocator/locator.py {}/{} < input.py > fragment.py'.format(fragment['classifier'], fragment['name']))

        f = open('fragment.py', 'r')
        data = f.read()
        f.close()

        fragment['fragment'] = data

    for fragment in t2['fragments']:
        f = open('input.py', 'w')
        f.write(text2)
        f.close()
        os.system('python PyFragmentLocator/locator.py {}/{} < input.py > fragment.py'.format(fragment['classifier'], fragment['name']))

        f = open('fragment.py', 'r')
        data = f.read()
        f.close()

        fragment['fragment'] = data

    result = []

    for fragment in t1['fragments']:
        found = False
        for f2 in t2['fragments']:
            if fragment['classifier'] == f2['classifier'] and fragment['name'] == f2['name'] and fragment['fragment'] == f2['fragment']:
                found = True

        result.append(found)

    if not result:
        return 0

    return len(filter(bool, result)) / float(len(result))

def getMatchCluster(cluster, text2):
    f = eval(f_name)
    return map(lambda member: f(csFlat[member], text2), cluster)

i = 0
clusters = {}

iterations = 0.0
for c in data:
    i += 1
    for f in cs[c]:
        print 'Checking', f,
        clusters[f] = {'files': [{'name': f, 'diffratios': [1]}]}
        for cluster in clusters:
            if f == cluster:
                continue
            diffratios = getMatchCluster(map(lambda fs: fs['name'], clusters[cluster]['files']), cs[c][f])
            mindiffratio = min(diffratios)
            if mindiffratio >= float(sys.argv[2]):
                clusters[cluster]['files'].append({'name': f, 'diffratios': diffratios + [1]})
                if mindiffratio < clusters[cluster].get('mindiffratio', 1):
                    clusters[cluster]['mindiffratio'] = mindiffratio
        print 'Done.'

for c in clusters.keys():
    if len(clusters[c]['files']) == 1:
        del clusters[c]

# complete diffratios

for c in clusters.keys():
    for i1, o1 in enumerate(clusters[c]['files']):
        for i2, o2 in enumerate(clusters[c]['files']):
            if i2 > i1:
                clusters[c]['files'][i1]['diffratios'].append(o2['diffratios'][i1])

for c in clusters.keys():
   origin = None
   for i, f in enumerate(clusters[c]['files']):
       url = 'http://101companies.org/resources/contributions/{}'.format(f['name'])
       github = json.loads(requests.get(url).text)['github']
       github = github.split('/')
       url = 'https://api.github.com/repos/{user}/{repo}/commits?path={path}'.format(user=github[3], repo=github[4], path='/'.join(github[7:]))
       info = json.loads(requests.get(url).text)
       info = map(lambda c: c['commit']['author'], info)
       first = sorted(info, key=lambda i: i['date'])[0]
       if not origin or origin['commit']['date'] > first['date']:
           origin = {
               'fileindex': i,
               'commit': first
           }
   clusters[c]['root'] = origin

for c in clusters.keys():
    for i, f in enumerate(clusters[c]['files']):
        clusters[c]['files'][i]['rootdiffratio'] = clusters[c]['files'][i]['diffratios'][clusters[c]['root']['fileindex']]
        clusters[c]['files'][i]['isroot'] = i == clusters[c]['root']['fileindex']

clusterlist = []
for c in clusters.keys():
    clusterlist.append(clusters[c])
clusters = clusterlist

with open(sys.argv[3], 'w') as outfile:
  json.dump(clusters, outfile, indent=4, separators=(',', ': '))
