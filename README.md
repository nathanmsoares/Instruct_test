# MagPy

A MagPy é uma API REST que gerencia uma coleção de projetos. Cada projeto tem um nome e uma lista de pacotes. 
Cada pacote tem um nome e uma versão.

Cada cadastro novo de um projeto recebe o nome e a lista de pacotes. Cada pacote da lista precisa obrigatoriamente especificar um nome, mas a versão é opcional.

O MagPy realiza a validação dos pacotes através de chamadas à API REST, 'https://pypi.org/pypi/{nome_do_pacote}/json', verificando se o pacote existe e se a versão passada existe também. A versão do pacote é opcional. Caso o usuário não passe a versão do pacote no JSON, a versão mais recente do pacote será adicionado.

Abaixo, alguns exemplos de chamadas que feitas nessa API:

```
POST /api/projects
{
    "name": "titan",
    "packages": [
        {"name": "Django"},
        {"name": "graphene", "version": "2.0"}
    ]
}
```
O código HTTP de retorno será o 201 e o corpo esperado na resposta é:
```
{
    "name": "titan",
    "packages": [
        {"name": "Django", "version": "3.2rc1" },  // Usou a versão mais recente
        {"name": "graphene", "version": "2.0" }   // Manteve a versão especificada
    ]
}
```

Se um dos pacotes informados não existir, ou uma das versões especificadas for inválida, um erro retornará.

Exemplo:
```
POST /api/projects
{
    "name": "titan",
    "packages": [
        {"name": "pypypypypypypypypypypy"},
        {"name": "graphene", "version": "1900"}
    ]
}
```
O código HTTP de retorno será o 400 e o corpo da resposta será:
```
{
    "error": "One or more packages doesn't exist"
}
```

Também é possível visitar projetos previamente cadastrados, usando o nome na URL:
```
GET /api/projects/titan
{
    "name": "titan",
    "packages": [
        {"name": "Django", "version": "3.2.5" },
        {"name": "graphene", "version": "2.0" }
    ]
}
```

E deletar projetos pelo nome:
```
DELETE /api/projects/titan
```

A MagPy é case sensitivity, veja abaixo dois JSONs iguals à leitura humana mas diferentes para a API:
```
{
    "name": "titan",
    "packages": [
        {"name": "Django", "version": "3.2.5" },
        {"name": "graphene", "version": "2.0" }
    ]
}
```

```
{
    "name": "Titan",
    "packages": [
        {"name": "Django", "version": "3.2.5" },
        {"name": "graphene", "version": "2.0" }
    ]
}
```

Observe o valor da chave 'name' nos dois JSONs, uma você verá { "name": "titan" } e na outra { "name": "Titan" }, para a MagPy são dois projetos distintos.
Fique atento ao case sensitivity.

# Utilidade

A MagPy é útil para empresas que desejam manter um histórico de seus projetos e acessivel à todos. Fornecendo informações das depedências de um projeto através de uma busca na API REST MagPy. Caso a pessoa não informar qual a versão que ela está usando, a API buscará a ultima versão do pacote, trazendo uma facilidade ao usuário.

# Testes Automatizados

Você pode realizar testes unitários utilizando o arquivo tests.py que te mostrará como funciona a MagPy.
Vá no diretório raiz do projeto, instale as depedências que se encontram no arquivo Pipfile, rode o comando "python manage.py test", então os testes unitários serão realizados.
Há um segundo arquivo para testes unitários. o arquivo 'tests-open.js'.
Você pode executar esses testes com o [k6](https://k6.io/). Para instalar o k6 basta [baixar o binário](https://github.com/loadimpact/k6/releases) para o seu sistema operacional (Windows, Linux ou Mac).

Para rodar os testes abertos, especifique a variável de ambiente "API_BASE" com o endereço base da API testada.

Exemplo de aplicação rodando no localhost na porta 8080:
```
k6 run -e API_BASE='http://localhost:8080/' tests-open.js
```

# Testes Manuais

Você pode utilizar o JSON abaixo como base e remover partes do json para os métodos post, put e patch. Desta forma você terá um maior conhecimento sobre a ferramenta.
Por exemplo, caso você utilize json abaixo.
```
PATCH /api/projects/titan
{
    "packages": [
        {"version": "3.2.5" }
    ]
}
```
Retornará o erro com o HTTP code 400 e o json abaixo.
```
{
    "error": "One or more packages doesn't exist"
}
```
