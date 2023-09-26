from datetime import datetime,timedelta,timezone
from flask_openapi3 import OpenAPI, Info, Tag
from flask import Flask, redirect, request, send_file,jsonify
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS,cross_origin
from pathlib import Path
from util import email,photo,cep
from PIL import Image
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies
from model import Session
from logger import logger
from schemas import *
from werkzeug.utils import secure_filename
from termcolor import colored

import requests
import os

info = Info(title="Token Service", version="1.0.0")

# Bearer Sample
bearer = {
  "type": "http",
  "scheme": "bearer"
}

security = [{"access_token": []}]
security_schemes = {"access_token": bearer}

app = OpenAPI(__name__, info=info, security_schemes=security_schemes)
CORS(app)

# cors = CORS(app,resources={r'/*':{'origins':'*'}})
app.config.from_object('config')
jwt = JWTManager(app)

home_tag = Tag(name="Token Service",
               description="Documentação da API do Token Service")

User_tag = Tag(
    name="User", description="Gestão dos usuários.")

Token_tag = Tag(
    name="Token", description="Gestão de acessos")

Photo_tag = Tag(
    name="Photo", description="Gestão de acesso do microserviço de fotos")

Email_tag = Tag(
    name="Email", description="Gestão de acesso do microserviço de e-mails")

Cep_tag = Tag(
    name="Cep", description="Gestão de busca de CEP")


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi/swagger, tela do swagger com a documentação do Token Service.
    """
    return redirect('/openapi/swagger')


#######################################################################################################################
# Gestão de usuário
#######################################################################################################################

# Inclusão do usuário
@app.post('/user/post', tags=[User_tag],responses={"200": UserViewSchema,  "409": UserErrorSchema,  "400": ErrorSchema})
def user_add(form:UserSchema):
    """Adiciona um novo usuário à base de dados.

    Retorna uma representação do usuário.
    """
    _user_email = form.user_email
    _user_login = form.user_login
    _user_password = form.user_password

    _session = Session()
    _new_user: User = _session.query(User).filter(User.user_email == _user_email).first()

    if not _new_user :

        _user = User(
            user_email=_user_email,
            user_login=_user_login,
            user_password=_user_password,
            user_activation_key =None,
            datetime_activation_key=None
            )

        logger.debug(colored(f"Adicionando o usuário '{_user_login}'", 'blue', attrs=['dark']))

        try:

            # adicionando o usuário
            _session.add(_user)
            _session.commit()
            logger.debug(colored(f"Adicionado o usuário '{_user_login}'", 'green', attrs=['bold']))
            return apresenta_User(_user), 200

        except IntegrityError as e:

            _error_msg = "Usuário de mesmo nome já salvo na base :/"
            logger.warning(colored(f"Erro ao adicionar o usuário '{_user_login}'. '{_error_msg}'", 'red', attrs=['bold']))
            return {"mensagem": _error_msg}, 400

        except Exception as e:

            _error_msg = "Não foi possível salvar novo usuário :/"
            logger.warning(colored(f"Erro ao adicionar o usuário '{_user_login}'. {e}", 'red', attrs=['bold']))
            return {"mensagem": _error_msg}, 400
    else:

        # _error_msg = "Usuário já cadastrado !"
        _error_msg = {
                "code": "error",
                "message": "Email já cadastrado",
                "data": {
                    "status":403
                },
            }
    
        logger.warning(colored(f"Usuário '{_user_login}' já cadastrado", 'red', attrs=['bold']))
        # return error_msg, 400  
        return _error_msg, 409   


# Retorna dados do usuário baseado no token
@app.get('/user/get',tags=[User_tag],responses={"200": TokenViewSchema,"409": ErrorSchema, "400": ErrorSchema},security=security)
@jwt_required(optional=False,locations="headers")
def user_by_token():
    """Retorna dados do usuário baseado no token.
    """

    return jsonify(
        user_id=current_user.id,
        user_email=current_user.user_email,
        user_login=current_user.user_login
    )


# Tratamento para recuperar a senha. Faz o envio de email para criar uma nova senha
@app.get('/user/password_lost', tags=[User_tag],responses={"200": EmailReturnSchema,  "409": ErrorSchema,  "400": ErrorSchema})
def api_password_lost(query: EmailPostSchema):
    """ Tratamento para recuperar a senha. 
    Faz o envio de email para criar uma nova senha.

    user_url - URL que será enviada no e-mail para o usuário clicar e alterar a senha.
    user_login - Login do usuário.
    user_email - E-mail onde será enviada a mensagem para alterar a senha.

    Essa rota faz a chamada do método que faz o envio do e-mail com uma chave unica que 
    deve ser validada, quando a aplicação chamar a rota /user/password_reset.

    O envio do e-mail é feito pelo microserviço de e-mail

    """

    _email_url =  app.config['EMAIL_URL'] ## Url do microseriço de e-mail
    _user_url =  query.user_url    
    _user_login = query.user_login
    _user_email = query.user_email

    # Chamada do método que faz o envio do e-mail com uma chave unica que deve ser validada,
    # quando a aplicação chamar a rota /user/password_reset.
    _response = email.api_password_lost(url_email=_email_url,
                                        user_login=_user_login,
                                        user_email=_user_email,
                                        user_url=_user_url)
    return _response


# Tratamento para salvar nova senha, com a chave enviada via email
@app.get('/user/password_reset', tags=[User_tag],responses={"200": EmailReturnSchema,  "409": ErrorSchema,  "400": ErrorSchema})
def api_password_reset(query: ResetPostSchema):
    """Tratamento para salvar nova senha.
    Com o link enviado via e-mail, o usuário é direcionado para um site onde pode cadastrar uma nova senha.
    
    user_password - Nova senha para ser cadastrada.
    user_login - Login do usuário.
    user_activation_key - Chave de autenticação que foi enviada no para o e-mail do usuário.
    
    """   

    _time_expiration =  float(app.config['PASSWORD_RESET_EXPIRATION_HOURS'])
    _user_login = query.user_login
    _user_password = query.user_password
    _user_activation_key = query.user_activation_key

    # Chamada do método que faz a validação da chave user_activation_key e salva a nova senha.
    _response = email.api_password_reset(time_expiration= _time_expiration,
                                    user_login=_user_login,
                                    user_password=_user_password,
                                    user_activation_key=_user_activation_key)
    return _response


#######################################################################################################################
# Gestão de acesso pelo token
#######################################################################################################################

# Retorna o token e o refresh token baseado no usuário e senha
@app.get('/token/get', tags=[Token_tag], responses=  {"200": TokenGetReturnSchema,"409": ErrorSchema, "400": TokenGetErrorSchema})
def login(query:TokenSchema):
    """Retorna o token e o refresh token baseado no usuário e senha.
    """

    _user_login =query.user_login
    _user_password = query.user_password

    try:

        # criando conexão com a base
        _session = Session()
        _user: User = _session.query(User).filter(
            User.user_login == _user_login and User.user_password == _user_password ).first()

        # user = Users.query.filter_by(user_login=user_login).one_or_none()
        if not _user : #or not user.check_password(user_password):
            return jsonify({"mensagem":"Usuário ou senha errados"}), 401

        _access_token = create_access_token(identity=_user)
        _refresh_token = create_refresh_token(identity=_user )

        return jsonify( user_email=_user.user_email,
                        user_login=_user.user_login,
                        token=_access_token, 
                        refresh_token=_refresh_token),200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# Retorna um novo token baseado no refresh token
@app.get('/token/refresh', tags=[Token_tag],responses={"200": TokenRefreshReturnSchema,  "409": ErrorSchema,  "400": ErrorSchema}, security=security)
@jwt_required(refresh=True,optional=True,locations="headers")
def refresh():
    """Retorna um novo token baseado no refresh token.
    """

    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)


# Valida o usuário com o token passado
@app.get('/token/validate', tags=[Token_tag],responses={"200": TokenValidateReturnSchema,  "409": ErrorSchema,  "400": ErrorSchema},security=security)
@jwt_required(optional=False,locations="headers")
def validate():
    """Valida o usuário com o token passado.
    """

    current_user = get_jwt_identity()
    return jsonify(user_id=current_user), 200

#######################################################################################################################
# Gestão da foto
#######################################################################################################################

# Faz o tratamento da imagem e o envio para o microserviço de fotos.
@app.post('/photo/post', tags=[Photo_tag],responses={"200": PhotoViewSchema, "409": ErrorSchema, "400": ErrorSchema},security=security)
@jwt_required(optional=False,locations="headers")
def api_photo_add():
    """Adiciona uma nova foto à base de dados.

    Retorna uma representação da foto.
    """
    # current_user = get_jwt_identity()
    _photo_user = current_user.id
    # print("photo_user")
    # print(photo_user)

    _photo_login = current_user.user_login
    # print("photo_login")
    # print(photo_login)

    if not _photo_user:
        _response = {'error': 'Informe o usuário.', 'status': 406}
        return jsonify(_response), 406

    _session = Session()
    _user_photo: User = _session.query(User).filter(
        User.id == _photo_user).first()

    if not _user_photo :
        return jsonify("Usuário não cadastrado"), 401

    _photo_url =  app.config['PHOTO_URL'] # Endereço do microserviço da foto
    
    _photo_descricao = request.form['photo_descricao']
    _photo_imagem = request.files['photo_imagem']
    _photo_logradouro = request.form['photo_logradouro']
    _photo_complemento = request.form['photo_complemento']
    _photo_bairro = request.form['photo_bairro']
    _photo_localidade = request.form['photo_localidade']
    _photo_uf = request.form['photo_uf']
    _photo_cep = request.form['photo_cep']
    
    _url = _photo_url+"/photo/post"

    # Verifica se o arquivo possui um nome e é uma extensão de imagem válida
    if _photo_imagem.filename == '' or not allowed_file(_photo_imagem.filename):
        return 'Nome de arquivo inválido ou extensão não permitida',409

    # Salva o arquivo no servidor
    _filename = os.path.join(app.config['UPLOAD_FOLDER'], _photo_imagem.filename)
    _photo_imagem.save(_filename)

    # Redimensiona a imagem para uma versão menor

    _extensions = _filename.rsplit('.', 1)[1].lower()
    _new_filename1000 = Path(_filename).stem+"_1000x1000."+_extensions

    _filename1000 =   os.path.join(app.config['UPLOAD_FOLDER'], _new_filename1000) 

    # print(" filename1000 ")
    # print(filename1000)

    _image = Image.open(_filename)
    _image.thumbnail((1000, 1000))


    # print(" e_pois do 1000 x 1000 filename")
    # print(filename1000)

    _image.save(_filename1000)
    _image.close()


    if os.getcwd() ==  '/app':
        _delete_file = os.getcwd()+"/"+ _filename
    else:
        _delete_file = os.getcwd()+"\\"+ _filename

    os.remove(_delete_file)

    _my_img = {'photo_imagem': open(_filename1000, 'rb')}
 
    _photo = {
        "photo_user": _photo_user,
        "photo_login": _photo_login,
        "photo_descricao": _photo_descricao,
        "photo_logradouro": _photo_logradouro,
        "photo_complemento": _photo_complemento,
        "photo_bairro": _photo_bairro,
        "photo_localidade": _photo_localidade,
        "photo_uf": _photo_uf,
        "photo_cep": _photo_cep
    }

   
    # Envio da imagem para o microserviço de fotos

    _response =  requests.post(_url, data=_photo, files=_my_img)

    _my_img['photo_imagem'].close()
    
    if os.getcwd() ==  '/app':
        _delete_file = os.getcwd()+"/"+ _filename1000
    else:
        _delete_file = os.getcwd()+"\\"+ _filename1000

    # Após o envio, apago a imagem na pasta temporária
    os.remove(_delete_file)

    return _response.json(),_response.status_code

# Faz a busca de uma foto via microserviço de fotos.
@app.get('/photo/get', tags=[Photo_tag],responses={"200": PhotoViewSchema, "409": ErrorSchema, "400": ErrorSchema},security=security)
@jwt_required(optional=False,locations="headers")
def api_photo_get(query: PhotoBuscaSchema):
    """Faz a busca pela foto a partir do id da photo.

    Retorna uma representação da foto.
    """
    
    _photo_id = query.photo_id
    _photo_url =  app.config['PHOTO_URL'] # Endereço do microserviço da foto

    # Chamada do método que faz a busca da foto a partir do id.
    return photo.api_photo_get(photo_id=_photo_id,photo_url=_photo_url)

# Faz a busca das fotos pelo usuário, página e total por página via microserviço de fotos.
@app.get('/photos/get', tags=[Photo_tag],responses={"200": UserViewSchema, "409": ErrorSchema, "400": ErrorSchema},security=security)
@jwt_required(optional=False,locations="headers")
def api_photos_get(query: PhotosBuscaSchema):
    """Faz a busca por todas as fotos cadastradas por usuário.

    Retorna uma listagem da representação das fotos de um usuário filtando pela página e total por página.
    """
    
    _photo_login = query.photo_login
    _photo_page = query.photo_page
    _photo_total = query.photo_total
    _photo_url =  app.config['PHOTO_URL'] # Endereço do microserviço da foto

    # Chamada do método que faz a busca das fotos pelo usuário, página e total por página.
    return photo.api_photos_get(photo_url=_photo_url,photo_login = _photo_login,
                                photo_page = _photo_page,photo_total = _photo_total)

# Faz o delete de uma foto via microserviço de fotos.
@app.delete('/photo/delete', tags=[Photo_tag],responses={"200": PhotoDelSchema, "409": ErrorSchema, "400": ErrorSchema},security=security)
@jwt_required(optional=False,locations="headers")
def api_photo_delete(query: PhotoBuscaSchema):
    """Deleta uma foto a partir do id informado.

    Retorna uma mensagem de confirmação da remoção.
    """

    _photo_id = query.photo_id
    _photo_url =  app.config['PHOTO_URL'] # Endereço do microserviço da foto
    
    # Chamada do método que faz o delete de uma foto.
    return photo.api_photo_delete(photo_id=_photo_id,photo_url=_photo_url)

# Faz a atualização de uma foto via microserviço de fotos.
@app.put('/photo/put', tags=[Photo_tag],responses={"200": PhotoViewSchema, "409": ErrorSchema, "400": ErrorSchema},security=security)
@jwt_required(optional=False,locations="headers")
def api_photo_put(query: PhotoPutSchema):
    """Atualiza uma foto na base de dados.
    
    Retorna uma representação da foto.
    """

    _photo_url =  app.config['PHOTO_URL'] # Endereço do microserviço da foto
    
    _photo_id = query.photo_id
    _photo_user=query.photo_user
    _photo_login=query.photo_login
    _photo_descricao=query.photo_descricao
    _photo_logradouro=query.photo_logradouro
    _photo_complemento=query.photo_complemento
    _photo_bairro=query.photo_bairro
    _photo_localidade=query.photo_localidade
    _photo_uf=query.photo_uf
    _photo_cep=query.photo_cep

    # Chamada do método que faz a atualização de uma foto.
    return photo.api_photo_put(photo_url=_photo_url,photo_id=_photo_id,photo_user=_photo_user,photo_login=_photo_login,
                               photo_descricao=_photo_descricao,photo_logradouro=_photo_logradouro,
                               photo_complemento=_photo_complemento,photo_bairro=_photo_bairro,photo_localidade=_photo_localidade,
                               photo_uf=_photo_uf,photo_cep=_photo_cep)

# Faz o inclusão do comentário da foto via microserviço de fotos.
@app.post('/photo/comment', tags=[Photo_tag],responses={"200": CommentResultSchema, "409": ErrorSchema, "400": ErrorSchema},security=security)
@jwt_required(optional=False,locations="headers")
def api_photo_comment():
    """Adiciona um novo comentário à foto na base de dados.

    Retorna uma representação do comentário.
    """


    _comment_author = current_user.user_login
    _comment_content = request.form['comment_content']
    _comment_post_id = request.form['comment_post_id']
    _photo_url =  app.config['PHOTO_URL'] # Endereço do microserviço da foto

    # Chamada do método que faz inclusão um novo comentário à foto.
    return photo.api_photo_comment(photo_url=_photo_url,comment_post_id=_comment_post_id,
                                   comment_author=_comment_author,comment_content=_comment_content)


#######################################################################################################################
# Gestão do CEP - Chamada da API externa
#######################################################################################################################

# Faz a busca de um enderço baseado no CEP
# Este é a chamada de uma API externa
@app.get('/cep/get', tags=[Cep_tag],responses={"200": CepResultSchema, "409": ErrorSchema, "400": CepErrorSchema},security=security)
@jwt_required(optional=False,locations="headers")
def api_cep_get(query:CepSchema):

    # comment_post_id = form.id
    _cep = query.cep

    if len(_cep)<8:
        error_msg = "O tamanhho do CEP deve ser 8 :/"
        return {
                "code": "error",
                "message": error_msg,
                "data": {
                    "status":403
                },
            }, 400   

    _cep_url =  app.config['CEP_URL'] # Endereço da API externa

    # Chamada do método que faz a busca do endereço pelo CEP.
    return cep.api_cep_get(cep_url=_cep_url,cep=_cep)


#######################################################################################################################
# Funções auxiliares
#######################################################################################################################

@jwt.user_identity_loader
def user_identity_lookup(user):

    return user if type(user) == int else user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    session = Session()
    return session.query(User).filter(User.id == identity).first()

@app.after_request
def refresh_expiring_jwts(response):

    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response

# Verifica se a extensão do arquivo é permitida
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



    