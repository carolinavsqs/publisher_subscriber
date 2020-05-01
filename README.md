# Arquitetura Base de Publisher e Subscriber

Este trabalho é um projeto para a disciplina de sistemas distribuídos cujo objetivo é o desenvolvimento de um minicurso sobre publicar/assinar, composto por uma parte teórica e outra parte prática. Todo seu desenvolvimento foi baseado no livro Sistemas Distribuídos: Conceitos e Projeto.

A implementação realizada nesse trabalho foi a baseada em tópico. Os nós dessa arquitetura são ao mesmo tempo *publicadores* e *assinantes* e se conectam a um único *broker* centralizado, que é o responsável pelo gerenciamento das mensagens trocadas. 

Para mais detalhes da implementação e arquitetura acesse os arquivos *minucurso.pdf* e *tutorial.pdf*, presente na raiz desse repositório.

## Funcionalidades

* Publicar mensagem:
  Navegue pelo menu para escolher em qual tópico publicar e escrever a mensagem a ser publicada

* Criar tópicos:
  Quando o nó publicar uma mensagem em um tópico ainda não existente, o *Broker* irá cria-lo.

* Listar tópicos disponíveis:
  Navegue pelo menu para solictar a lista de tópicos disponíveis naquele momento

* Listar tópicos escritos pelo nó:
  Navegue pelo menu para solictar a lista de tópicos escrito pelo nó solicitante

* Assinar um tópico:
  Navegue pelo menu para escolher um tópico para se escrever

* Cancelar uma assinatura:
  Navegue pelo menu para receber a lista de tópicos escritos e selecionar o que deseja desescrever

## Requisitos

* Python3

* PostgreSQL

* psycopg2:

`pip3 install psycopg2`

## Como executar

### Configurando a base de dados

Crie o banco de dados: 

`createdb <nome_do_banco>`

Restaure o esquema do banco com o dump publisher_subscriber:

`pg_restore <nome_do_banco> publisher_subscriber`

Altere as informações de login do banco no código do broker.py

`con = psycopg2.connect(host='127.0.0.1', database='publisher_subscriber', user='postgres', password='suasenha')`


### Iniciar o Broker:

`python3 servidor.py`

Por padrão o *Broker* está para ser usado em rede local. Para outras situações é necessário mudar o HOST defino no início do código. O mesmo se aplica para a porta:

```
HOST = 'localhost'
PORT = 1232
```

### Iniciar os nós:

`python3 node.py`

Adeque o HOST e a Porta para combinar com o do *Broker*:

```
HOST = 'localhost'
PORT = 1232
```


