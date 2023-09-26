
from flask import request, jsonify
from model.user import User
from model import Session
import hashlib
import time
from datetime import datetime, timedelta
import requests
from werkzeug.urls import url_fix

# Método que monta o corpo do e-mail com uma chave unica que deve ser validada, 
# quando a aplicação chamar a rota /user/password_reset.
def api_password_lost(url_email:str,user_login:str,user_email:str,user_url:str):

    # print("Passou aqui api_password_lost antes")

    _url = url_email 

    if not user_login:
        response = {'error': 'Informe o email ou login.', 'status': 406}
        return jsonify(response), 406

    _session = Session()
    _user_reset: User = _session.query(User).filter(
        User.user_email == user_email).first()

    if not _user_reset :
        return jsonify("Usuário não cadastrado"), 401


    # Combina o ID do usuário e um timestamp atual para criar uma chave única
    _key_data = f"{_user_reset.id}:{int(time.time())}"


    # Uso de uma função de hash para criar uma hash da chave
    _key_hash = hashlib.sha256(_key_data.encode()).hexdigest()

    # Guarda a chave e o horário que ela foi gerada
    _user_reset.user_activation_key = _key_hash
    _user_reset.datetime_activation_key = datetime.now()

    _session.commit()

    # Montagem do corpo do e-mail
    _message = "Utilize o link abaixo para resetar a sua senha:\n"

    _url_ = f"{user_url}/?key={_key_hash}&login={user_login}"
    _url_ = url_fix(_url_)
   
    _body = _message + _url_
 
    # print("body")
    # print(_body)

    return  send_email(_url,user_email,_body)

# Método que faz o envio do e-mail com a chave unica.
def send_email(url:str,user_email:str,body:str):

    _email = {
        "to_email": user_email,
        "subject": 'Password Reset',
        "body": body,
    }

    _response =  requests.post(url, data=_email)
    return _response.json()

# Método que faz a validação da chave user_activation_key e salva a nova senha.
def api_password_reset(time_expiration:float,
                        user_login:str,
                        user_password:str,
                        user_activation_key:str):

    # print("Passou aqui api_password_lost antes")

    _session = Session()
    _user_reset: User = _session.query(User).filter(
        User.user_login == user_login).first()

    # Validação do usuário e da chave.
    if not _user_reset :
        _msg = "Usuário não cadastrado"
        return {"mensagem": _msg} , 401

    if _user_reset.user_activation_key == None or _user_reset.datetime_activation_key == None:
        _response = {'message': 'Usuário sem token.'}
        return jsonify(_response)


    # Validação da chave.
    _str_data = str(_user_reset.datetime_activation_key)
    _str_data = datetime.strptime(_str_data, '%Y-%m-%d %H:%M:%S.%f')

    _data_expiration = _str_data + timedelta(hours=time_expiration)
  
    if _data_expiration<datetime.now():
        _response = {'message': 'Token expirado.'}
        return jsonify(_response)

    if user_activation_key!=_user_reset.user_activation_key:
        _response = {'message': 'Token incorreto.'}
        return jsonify(_response)


    # Salva nova senha e limpa a chave.
    _user_reset.user_password = user_password
    _user_reset.datetime_activation_key = datetime.now()
    _user_reset.user_activation_key = None
    _user_reset.datetime_activation_key = None
    
    _session.commit()

    _response = {'message': 'Senha alterada.'}

    return jsonify(_response)

