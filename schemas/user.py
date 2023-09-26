# from pydantic import BaseModel
from typing import Any, List
from model.user import User
from datetime import datetime


from pydantic import BaseModel, Json, ValidationError

class Login(BaseModel):
    """ Define como um usuário será retornado.
    """
    user_login: str 
 

class Password(BaseModel):
    """ Define como um usuário será retornado.
    """
    user_password: str 
 
class AnyJsonModel(BaseModel):

    result = {
        "user_login": str,
        "user_password": str,
    }
    # json_obj: Json[result]

    dict_exemplo: dict = result

class CommentSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a inclusão de um comentário. 
    """

    comment_post_id: int = 0
    comment_author: str = "comment_author"
    comment_content: str = "comment_content"

class CommentResultSchema(BaseModel):
    """ Define como deve ser a estrutura que retorna um comentário. 
    """

    comment_post_ID: int 
    comment_author: str 
    comment_date: str 
    comment_date_gmt: datetime 
    comment_content: datetime 


class CepSchema(BaseModel):
    """ Define como um usuário deve ser inserido.
    """
    cep: str = "05516040"


class CepResultSchema(BaseModel):
  
      cep: str
      logradouro:str
      complemento: str
      bairro: str
      localidade: str
      uf: str
      ibge: str
      gia: str
      ddd: str
      siafi: str
    

class UserSchema(BaseModel):
    """ Define como um usuário deve ser inserido.
    """
    user_login: str = "Usuario"
    user_email: str = "E-mail"
    user_password: str = "Password"

class UserBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca. 
        Será feita apenas com base no id do usuário.
    """
    id: int = 0  # Id do usuário

class UserPostSchema(BaseModel):
    """ Define como um usuário será retornado.
    """
    mensagem: str
    id: int
    user_login: str 
    user_email: str
    user_password: str

class UserErrorSchema(BaseModel):
    """ Define como um usuário deve ser inserido.
    """

    
    code:str =  "error",
    data:str = {"status": 403},
    message:str= "Email já cadastrado"
    

class CepErrorSchema(BaseModel):
    """ Define como um usuário deve ser inserido.
    """

    
    code:str =  "error",
    data:str = {"status": 403},
    message:str= "O tamanhho do CEP deve ser 8 :/"
    



class app(BaseModel):
    """ Define como um usuário será retornado.
    """

    user_login: Login
    user_password: Password


class TokenSchema(BaseModel):
    """  Define como deve ser a estrutura que representa a busca do token. 
    """

    user_login: str 
    user_password: str

class TokenGetReturnSchema(BaseModel):
    """ Define como um usuário será retornado.
    """

    user_login: str 
    user_email: str
    token: str 
    refresh_token: str

class TokenGetErrorSchema(BaseModel):
    """ Define como um erro será retornado.
    """

    error: str


class TokenRefreshReturnSchema(BaseModel):
    """ Define como o token será retornado.
    """

    access_token: str

class TokenValidateReturnSchema(BaseModel):
    """ Define como o token será retornado.
    """

    user_id: int


class EmailPostSchema(BaseModel):
    """ Define como deve ser a estrutura de envio de e-mail para alterar a senha.
    user_url - URL que será enviada no e-mail para o usuário clicar e alterar a senha.
    user_login - Login do usuário.
    user_email - E-mail onde será enviada a mensagem para alterar a senha.
    """
    user_url: str 
    user_login: str
    user_email: str 


class PhotoBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca de uma foto. 
        Será feita apenas com base no photo_id da foto.
    """
    photo_id: int = 0  # Id da foto

class PhotoSchema(BaseModel):
    """ Define como um usuário será retornado.
    """
    # photo_photo:str
    photo_descricao: str 


class ResetPostSchema(BaseModel):
    """ Define como um usuário será retornado.
    """

    user_login: str 
    user_password: str
    user_activation_key: str


class PhotoPutSchema(BaseModel):
    """ Define como uma foto será retornada.
    """
    photo_id: int
    photo_user: int
    photo_descricao: str
    photo_login: str  # foto
    photo_logradouro: str  # descrição do cômodo
    photo_complemento: str  # descrição do cômodo
    photo_bairro: str  # descrição do cômodo
    photo_localidade: str  # descrição do cômodo
    photo_uf: str  # descrição do cômodo
    photo_cep: str  # descrição do cômodo
    

class BasicReturnSchema(BaseModel):
    """ Define como um usuário será retornado.
    """
    mensagem: str

class EmailReturnSchema(BaseModel):
    """ Define como um usuário será retornado.
    """
    mensagem: str

class UserViewSchema(BaseModel):
    """ Define como um usuário será retornado.
    """
    id: int
    user_login: str
    user_email: str
    user_password: str 

class PhotoViewSchema(BaseModel):
    """ Define como uma foto da será retornada.
    """
    photo_id: int
    photo_user: int
    photo_nome: str
    photo_descricao: str
    photo_login: str  
    photo_logradouro: str  
    photo_complemento: str  
    photo_bairro: str  
    photo_localidade: str  
    photo_uf: str  
    photo_cep: str  
   

class PhotosBuscaSchema(BaseModel):
    """ Define como deve ser a estrutura que representa a busca das fotos de um usuário. 
        Será feita apenas com base na photo_login, photo_page e photo_total da foto.
    """
    photo_login: str  # Id da foto
    photo_page: int = 0  # Id da foto
    photo_total: int = 0  # Id da foto
    
class PhotoDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma exclusão
        de remoção.
    """
    mensagem: str = "Foto removida"
    photo_id: int


class TokenViewSchema(BaseModel):
    """ Define como um usuário será retornado.
    """
    user_id: int
    user_email: str
    user_login: str

class ListagemUsersSchema(BaseModel):
    """ Define como uma listagem de usuários será retornada seguindo o schema definido em
        UserViewSchema.
    """
    Users: List[UserViewSchema]


class UserDelSchema(BaseModel):
    """ Define como deve ser a estrutura do dado retornado após uma requisição
        de remoção.
    """
    mensagem: str
    user_login: str
    user_email: str 
    user_password: str 

def apresenta_User(user: User):
    """ Retorna uma representação do usúario.
    """
    result = {
            "id": user.id,
            "user_login": user.user_login,
            "user_email": user.user_email,
            "user_password": user.user_password,
        }
    return result


def apresenta_Users(users: List[User]):
    """ Retorna uma listagem de uma representação do usúario.
    """
    result = []
    for User in users:

        result.append(

            {
                "id": User[0].id,
                "User": User[1].user_login,
                "E-mail": User[2].user_email,
                "Password": User[4].user_password,
            }
        )

    return {"Users": result}
