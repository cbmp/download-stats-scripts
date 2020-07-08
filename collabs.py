import json
import requests
import time

def getPublications(data):
    for item in data:
        name = item["name"]
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=$%s&retmax=800&retmode=json" % (item["query"])
        item["pubs"] = requests.get(url).json()['esearchresult']['idlist']
        time.sleep(2)
    return data



if __name__ == "__main__":
    rawData = [
        {
            'name': 'Haibe-Kains', 
            'query': 'Haibe-Kains+Benjamin%5BAU%5D',
            'pubs': [],
        }, {
            'name': 'Pugh',
            'query': 'Pugh+T%5BAU%5D+AND+%28Marziali%5BAU%5D+OR+Marra%5BAU%5D+OR+Meyerson%5BAU%5D+OR+Getz%5BAU%5D+OR+Rehm%5BAU%5D+OR+Taylor%5BAU%5D+OR+Tsongalis%5BAU%5D%29+OR+%28Pugh+TJ%5BAU%5D+AND+Toronto%5BAD%5D%29',
            'pubs': [],
        }, {
            'name': 'Hoffman',
            'query': 'Hoffman%20Michael%20M%5Bau%5D%20OR%20Hoffman%20Michael%20M%5Bir%5D%20OR%20International%20Chicken%20Genome%20Sequencing%20Consortium%5Bcn%5D',
            'pubs': [],
        }, {
            'name': 'Liu',
            'query': 'Liu+G%5BAU%5D+AND+Toronto%5BAD%5D+OR+23291255%5BPMID%5D+NOT+%28Liu+GC%5BAU%5D+OR+Liu+GY%5BAU%5D+OR+Liu+GK%5BAU%5D%29',
            'pubs': [],
        }, {
            'name': 'Minden',
            'query': 'Minden+MD%5BAU%5D+OR+%28Minden+M%5BAU%5D+AND+Toronto%29+OR+8401592%5BPMID%5D',
            'pubs': [],
        }, {
            'name': 'Moran',
            'query': 'Moran+MF%5BAU%5D+OR+%28Moran+M%5BAU%5D+AND+Pawson+T%5BAU%5D%29',
            'pubs': [],
        },
        {
            'name': 'Xu',
            'query': '(Xu%2C%20Wei%5BFull%20Author%20Name%5D%20OR%20Wei%2C%20Xu%5BFull%20Author%20Name%5D%20OR%20Xu%2C%20Wei%5BFull%20Investigator%20Name%5D%20OR%20wei%20xu%5BAuthor%5D%20OR%20wei%20xu%5BInvestigator%5D)%20AND%20((princess%5BAll%20Fields%5D%20AND%20margaret%5BAll%20Fields%5D)%20AND%20toronto%5BAll%20Fields%5D)',
            'pubs': [],
        },
    ]

    data = getPublications(rawData)
    json_str = json.dumps(data)
    f = open("collabStats.json", "w") 
    f.write(json_str)
    f.close()