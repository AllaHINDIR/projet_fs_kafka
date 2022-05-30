import json
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
sparql = SPARQLWrapper(endpoint)

def get_occupation():

    sparql.setQuery("""SELECT DISTINCT ?profession ?professionLabel ?linkcount  WHERE {
      {
        SELECT DISTINCT ?profession ?professionLabel ?linkcount WHERE {
          ?profession wdt:P31 wd:Q28640.
          ?profession wikibase:sitelinks ?linkcount.
          FILTER (10 <= ?linkcount).
          SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".}
        }
      }
    }
    ORDER BY DESC (?linkcount)""")

    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    print("[INFO] Getting Occupations")
    return results
