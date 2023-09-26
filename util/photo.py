import requests


# Método que faz a busca da foto a partir do id.
def api_photo_get(photo_id:int,photo_url:str):

    # print("Passou aqui api_photo_get antes")

    # Montagem da URL
    _url = photo_url+"/photo/get?photo_id="+str(photo_id)
    _response =  requests.get(_url)

    return _response.json(),_response.status_code

# Método que faz a busca das fotos pelo usuário, página e total por página.
def api_photos_get(photo_url:str,photo_login:str,photo_page:int,photo_total:int):

    # print("Passou aqui api_photo_get antes")
    
    # Montagem da URL
    _url = photo_url+"/photos/get?photo_login="+str(photo_login)+"&photo_page="+str(photo_page)+"&photo_total="+str(photo_total)
    _response =  requests.get(_url)

    return _response.json(),_response.status_code

# Método faz o delete de uma foto.
def api_photo_delete(photo_id:int,photo_url:str):

    # print("Passou aqui api_photo_delete antes")
    
    # Montagem da URL
    _url = photo_url+"/photo/delete?photo_id="+str(photo_id)
    _response =  requests.delete(_url)

    return _response.json(),_response.status_code

# Método que faz inclusão um novo comentário à foto
def api_photo_comment(photo_url:str,comment_post_id:int,comment_author:str,comment_content:str):

    # print("Passou aqui api_photo_comment antes")

    # Montagem da URL
    _url = photo_url+"/photo/comment"
    
    _comment = {
        "comment_post_id": comment_post_id,
        "comment_author": comment_author,
        "comment_content": comment_content
    }

    # print(f"Antes de enviar para a url '{url}'")
   
    _response =  requests.post(_url, data=_comment)

    return _response.json(),_response.status_code

# Método que faz a atualização de uma foto.
def api_photo_put(  photo_url:str,photo_id:int,photo_user:str,photo_descricao:str,
                    photo_login:str,photo_logradouro:str,photo_complemento:str,photo_bairro:str,
                    photo_localidade:str,photo_uf:str, photo_cep:str):

    # print("Passou aqui api_photo_put antes")

    # Montagem da URL
    _url = photo_url+"/photo/put"
    
    _photo = {
        "photo_id": photo_id,
        "photo_user": photo_user,
        "photo_descricao": photo_descricao,
        "photo_login": photo_login,
        "photo_logradouro": photo_logradouro,
        "photo_complemento": photo_complemento,
        "photo_bairro": photo_bairro,
        "photo_localidade": photo_localidade,
        "photo_uf": photo_uf,
        "photo_cep": photo_cep
    }

    # print(f"Antes de enviar para a url '{url}'")
    # print(photo)

    _response =  requests.put(_url, data=_photo)

    return _response.json(),_response.status_code
