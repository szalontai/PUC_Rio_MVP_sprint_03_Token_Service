# Componente C - Microserviço de gestão de acesso via token

Este projeto faz parte do material didático da Disciplina **Arquitetura de Software - Sprint 3** 

O objetivo desta API é a gestão de acesso, controle de usuário, acesso aos microservicçs de gestão de fotos, gestão de e-mail e a API externa B - VIACEP, que faz e busca de CEP´s, seguindo o estilo REST.

No arquivo  `.env`   estão contidos oa valores dos parâmetros EMAIL_URL, PHOTO_URL e CEP_URL, que são respectivamente o endereços dos microserviços de gestão de e-mail, gestão de fotos e a API externa de busca de CEP.


---
### Instalação


Será necessário ter todas as libs python listadas no `requirements.txt` instaladas.
Após clonar o repositório, é necessário ir ao diretório raiz, pelo terminal, para poder executar os comandos descritos abaixo.

> É fortemente indicado o uso de ambientes virtuais do tipo [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html).

Para gerar o arquivo `requirements.txt` rode o comando abaixo.

```
(env)$ pip freeze > requirements.txt
```


```
(env)$ pip install -r requirements.txt
```

Este comando instala as dependências/bibliotecas, descritas no arquivo `requirements.txt`.

---
### Executando o servidor


Para executar a API  basta executar:

```
(env)$ flask run --host 0.0.0.0 --port 5020
```

Em modo de desenvolvimento é recomendado executar utilizando o parâmetro reload, que reiniciará o servidor
automaticamente após uma mudança no código fonte. 

```
(env)$ flask run --host 0.0.0.0 --port 5020 --reload
```

---
### Acesso no browser

Abra o [http://localhost:5020/#/](http://localhost:5020/#/) no navegador para verificar o status da API em execução.

---
## Como executar através do Docker

Certifique-se de ter o [Docker](https://docs.docker.com/engine/install/) instalado e em execução em sua máquina.

Navegue até o diretório que contém o Dockerfile e o requirements.txt no terminal.
Execute **como administrador** o seguinte comando para construir a imagem Docker:

```
$ docker build -t token-service .
```

Uma vez criada a imagem, para executar o container basta executar, **como administrador**, seguinte o comando:

```
$ docker run -p 5020:5020 token-service
```

Uma vez executando, para acessar a API, basta abrir o [http://localhost:5020/#/](http://localhost:5020/#/) no navegador.

