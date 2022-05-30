import pysolr
solr = pysolr.Solr('http://localhost:8983/solr/core_2')
"""
    Cette fonction consiste à stocker le id et l'url d'une image 
    dans solr...
"""

def saveImageInSolr(idImage,urlImage):
    try :
        Images = []
        dataImage = {}
        dataImage['idImage'] = idImage
        dataImage['urlImage'] = urlImage
        Images.append(dataImage)
        solr.add(Images)
        print('[INFO] Image stockée dans Solr')
    except Exception as e:
        print(e)

"""
    Cette fonstion supprime une image dans Solr en utilisant le id par lequel elle 
    était stockée dans mongodb...
"""
def deleteImageById(idImage):
    try :
        result = solr.search('idImage:' + idImage)
        solr.delete(id=result.docs[0]['id'])
    except Exception as e:
        print(e)

