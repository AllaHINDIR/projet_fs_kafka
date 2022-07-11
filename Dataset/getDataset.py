import json
import time


from SPARQLWrapper import SPARQLWrapper, JSON
import concurrent.futures

from Dataset import getOccupation

endpoint = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
sparql = SPARQLWrapper(endpoint)


def extract_string(string):
    """
    Cette fonction consiste à extraire un text d'une chaine de caracteres.
    :param string: la chaine de caracteres.
    :return: la partie extraite
    """
    try:
        found = string.removeprefix("http://www.wikidata.org/entity/")
        print(found)
        return found
    except AttributeError:
        pass


def get_persons(occupation):
    """
    Cette fonction permet de récupérer les célébrités dont l'occupation est donnée en parametre.
    :param occupation: la profession.
    :return: un objet JSON qui contient toutes les célébrités récupérés.
    """
    sparql.setQuery("""
    SELECT DISTINCT ?human ?humanLabel ?humanDescription ?birth ?linkcount
    WHERE
    {
      {
      SELECT ?human ?humanLabel ?humanDescription ?birth ?linkcount WHERE {
      VALUES ?profession {wd:""" + extract_string(occupation['profession']['value']) + """}
      ?human wdt:P31 wd:Q5.    
      ?human wdt:P106 ?profession.
      ?human wdt:P569 ?birth.
      ?human wikibase:sitelinks ?linkcount.
      FILTER("1950-01-01"^^xsd:dateTime <= ?birth).
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }
      }
      LIMIT 3000
    }
    }
    ORDER BY DESC (?linkcount)
    LIMIT 200

    """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print(
        "----------------------------- " + occupation['professionLabel']['value'] + " --------------------------------")
    # pprint(results)
    return results


def get_persons_static(occupation):
    """
    Cette fonction permet de récupérer les célébrités dont l'occupation est donnée en parametre.
    :param occupation: la profession.
    :return: un objet JSON qui contient toutes les célébrités récupérés.
    """
    sparql.setQuery("""
    SELECT DISTINCT ?human ?humanLabel ?humanDescription ?birth ?linkcount
    WHERE
    {
      {
      SELECT ?human ?humanLabel ?humanDescription ?birth ?linkcount WHERE {
      VALUES ?profession {wd:""" + occupation + """}
      ?human wdt:P31 wd:Q5.    
      ?human wdt:P106 ?profession.
      ?human wdt:P569 ?birth.
      ?human wikibase:sitelinks ?linkcount.
      FILTER("1970-01-01"^^xsd:dateTime <= ?birth).
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }
      }
      LIMIT 3000
    }
    }
    ORDER BY DESC (?linkcount)
    LIMIT 1

    """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print("----------------------------- " + occupation+ " --------------------------------")
    # pprint(results)
    return results

def main2() :
        """
        Programme principal responsable sur le lancement de la recherche des célébrités sur Wikidata en utilisant
        un nombre défini des threads. Apres la récupération des 6 premiere professions les plus célébres sur Wikidata.
        :return: un json contenant les informations des célébrités de chaque profession.
        """

        start = time.time()
        occupations = getOccupation.get_occupation()
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as process:
            r = process.map(get_persons, [occupations['results']['bindings'][0], occupations['results']['bindings'][1],
                                        occupations['results']['bindings'][2], occupations['results']['bindings'][3],
                                        occupations['results']['bindings'][4], occupations['results']['bindings'][5]])

        end = time.time()
        print(end - start)
        r1 = list(r)
        print(len(r1))
        return r1


def main() :
    """
    Programme principal responsable sur le lancement de la recherche des célébrités sur Wikidata en utilisant
    un nombre défini des threads.
    Ici le choix des professions est statique : fooballeur, chanteur, poloticien, rappeur, ecrivien, animateur, physicien.
    :return: un json contenant les informations des célébrités de chaque profession.
    """


    start = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as process:
        r = process.map(get_persons_static, ["Q36180","Q169470","Q13590141","Q937857","Q177220","Q82955","Q2252262"])

    end = time.time()
    print(end - start)
    r1 = list(r)
    print(len(r1))
    return r1
