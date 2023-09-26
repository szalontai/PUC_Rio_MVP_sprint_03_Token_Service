import requests

# Método que faz a busca do endereço pelo CEP.
def api_cep_get(cep_url:str,cep:str):

    # print("Passou aqui api_cep_get antes")

    # Montagem da URL
    _url = cep_url+cep+"/json/"
    _response =  requests.get(_url)

    return _response.json(),_response.status_code

