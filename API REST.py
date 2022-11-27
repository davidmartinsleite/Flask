from itertools import count
from typing import Optional
from flask import Flask, request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage  # ele consegue colocar dados em memorio


server = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='apredizagem de API')  # aqui ele cria uma pagina com todas as
# APIs disponiveis para testalas e ver seus funcionamentos
spec.register(server)
# database = TinyDB('database.json')  # criamos o banco de dados para a aplicação aqui ele armazena os dados
database = TinyDB(storage=MemoryStorage)  # toda vida que a aplicação reiniucia o banco começa novamente do ZERO
contagem = count()  # cria uma contagem automatica, ele usa o função 'next'


# isso não é uma classe de orientação a objeto, isso é uma data class (uma classe só visual)

class QueryPessoa(BaseModel):
    id: Optional[int]
    nome: Optional[str]
    idade: Optional[int]


class Pessoa(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(contagem))  # o lambda chama a função next
    nome: str
    idade: int


class Pessoas(BaseModel):
    pessoas: list[Pessoa]
    count: int


# GET
@server.get('/pessoas')
@spec.validate(
    query=QueryPessoa,
    resp=Response(HTTP_200=Pessoas)
)  # caso tenha sucesso (200)
def buscar_pessoas():
    '''Retorna todas as pessoas da base de dados.'''
    query = request.context.query.dict(exclude_none=True)
    # breakpoint()  # serve para debug, ele vai travar
    todas_as_pessoas = database.search(
        Query().fragment(query)
    )
    return jsonify(  # aqui é oq ele retorna, nesse caso retorna o 'todas_as_pessoas'
        Pessoas(
            pessoas=todas_as_pessoas,
            count=len(todas_as_pessoas)
        ).dict()  # vamos converter para um dicionario e ver como via ser o comportamento
    )
# GET 02
@server.get('/pessoas/<int:id>')
@spec.validate(resp=Response(HTTP_200=Pessoa))  # caso tenha sucesso (200)
def buscar_pessoa(id):
    '''Retorna uma pessoa da base de dados.'''
    try:
        pessoa = database.search(Query().id == id)[0]
    except IndexError:
        return {'massage': 'Pessoa não encontrada'}, 404  # aqui ele retorna o não encontrado
    return jsonify(pessoa)

# POST
@server.post('/pessoas')  # aqui vamos enviar um dado para o server, ele vai ser no mesmo endpoint pessoas
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_201=Pessoa))  # precisamos receber o corpo da requisição
# aqui ele vai requisitar Pessoa
def inserir_pessoa():
    '''Insere uma Pessoa no banco de dados.'''  # a docstring aparece no sistema
    body = request.context.body.dict()
    database.insert(body)  # inserimos os dados do TinyDB
    return body


# PUT
@server.put('/pessoas/<int:id>')  # ele passo o 'id' que é um interio da pessoa
@spec.validate(  # precisamos gantir que o id tenha o retorno certo
    body=Request(Pessoa), resp=Response(HTTP_200=Pessoa)
)
def altera_pessoa(id):  # vamos alterar os registros baseado no 'id'
    Pessoa = Query()    # vamos fazer a guery pelo tinyDB
    body = request.context.body.dict()
    database.update(body, Pessoa.id == id)  # vou mandar o update com o mesmo id q mandamos na rota
    return jsonify(body)
# agora temos um jeito de mudar os registros baseado na id


# DELET
@server.delete('/pessoas/<int:id>')  # ele passo o 'id' que é um interio da pessoa
@spec.validate(resp=Response('HTTP_204'))  # ele n precisa do 'body', ele n precisa receber nqm
def deleta_pessoa(id):                     # perceba que o retorno é 204
    Pessoa = Query()
    database.remove(Pessoa.id == id)  # ele remove com base no ID
    return jsonify('deletado')



server.run()

# para usar o httpie use o comando "http get http://localhost:5000/pessoas"

# para usar o SWAGGER use o link: http://127.0.0.1:5000/apidoc/swagger
# NOTA: com o servidor aberto

# caso queira inserir um dado pelo proprio httpie pode fazer assim:
# http post http://localhost:5000/pessoas id=2 idade=36 nome=Su
