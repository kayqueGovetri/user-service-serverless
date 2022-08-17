
# User service serverless

Um modelo serverless para um microsserviço genérico de usuários para qualquer sistema.



## Pré-requisitos
- Python 3
- SAM
- AWS CLI
- Docker
    

## Instalação

### Ambiente de desenvolvimento 
Pode utilizar o comando dev: 

```bash
    make dev
```

Ou se preferir os seguintes comandos: 

```bash
    pip install -r requirements.txt
    pip install -r requirements_dev.txt
	pre-commit install
```

### Ambiente de produção
Pode utilizar o comando **prod**:
```bash
    make prod
```

Ou se preferir os seguintes comandos: 

```bash
    pip install -r requirements.txt
```


## Rodando localmente

Clone o projeto

```bash
  git clone https://github.com/kayqueGovetri/user-service-serverless
```

Vá para a pasta do projeto.

```bash
  cd user-service-serverless
```

Install dependencies

```bash
  make dev
```

Start the server

```bash
  make start
```


## API Reference

#### Cadastro de usuário

```https
  POST /service/user/signup
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `username` | `string` | **Required**. Nome do usuário |
| `password` | `string` | **Required**. Senha do usuário |
| `email` | `string` | **Required**. Email do usuário |


#### Login de usuário

```http
  POST /service/user/login
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `email`      | `string` | **Required**. Email do usuário |
| `password`      | `string` | **Required**. Senha do usuário |


#### Atualizar o usuário

```http
  PUT /service/user
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id do usuário |
| `username`      | `string` | Nome do usuário |
| `email`      | `string` | Email do usuário |
| `password`      | `string` | Senha do usuário |



#### Deletar o usuário

```http
  DELETE /service/user
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id do usuário |

#### Capturar um usuário

```http
  GET /service/user/<id>
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Required**. Id do usuário |


#### Capturar vários usuários

```http
  GET /service/users?limit=&last_evaluated_key=&
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `limit`      | `string` | **Required**. Limite de retorno em cada pagina |
| `last_evaluated_key`      | `string` | Token para capturar os dados da próxima pagina |
| `page`      | `string` | **Required**. Número da página a ser capturada  |


## Tech Stack

**Server:** Python, API Gateway


## Deploy no ambiente de desenvolvimento

Para fazer o deploy em dev é necessário possuir os seguintes requisitos:

- Ter as variáveis de acesso ao ambiente da AWS no computador (.aws/credentials).

```bash
  make deploy
```


## Rodando os testes

Para rodar os testes basta rodar o comando

```bash
  make test
```

Para averiguar a porcentagem de cobertura dos testes basta rodar
```bash
  make test-coverage
```
## Authors

- [@kayqueGovetri](https://www.github.com/kayqueGovetri)

