
# dataset of the populare peapole in WikiData
from Dataset import getDataset
from storage import connexion,celebrity_schema

def get_mongo_name_celebrities() :
    celebritys = []
    try :
        connexion.get_connexion()
        for celebrity in celebrity_schema.Celebrity.objects:
            celebrity_dic = {}
            celebrity_dic['name'] = celebrity.name
            celebrity_dic['profession'] = celebrity.categorie
            celebritys.append(celebrity_dic)
    except Exception as e:
        print(e)
    return celebritys

def get_new_name_celebrities() :
    celebritys = []
    celebritys_name = []
    try :
        connexion.get_connexion()
        list_categorie_celebritie = getDataset.main()
        for categorie in list_categorie_celebritie:
            for element in categorie['results']['bindings']:
                celebrity = {}
                if element['humanLabel']['value'] not in celebritys_name and celebrity_schema.Celebrity.objects(name=element['humanLabel']['value']).count() == 0:
                    celebrity['name'] = element['humanLabel']['value']
                    celebrity['profession'] = element['humanDescription']['value']
                    celebritys_name.append(element['humanLabel']['value'])
                    celebritys.append(celebrity)
        print(celebritys)
        print(len(celebritys))

    except Exception as e:
        print(e)
    return celebritys

