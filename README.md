[![Build Status](https://travis-ci.org/IvanBrasilico/raspa-preco.svg?branch=master)](https://travis-ci.org/IvanBrasilico/raspa-preco) [![codecov](https://codecov.io/gh/IvanBrasilico/raspa-preco/branch/master/graph/badge.svg)](https://codecov.io/gh/IvanBrasilico/raspa-preco)

# raspa-preco
Raspador de sites e-commerce  - pesquisa de preço de produto por parâmetros e montagem de tabelas e dossiês comparativos

O foco não é comparação de preços (a exemplo de google shopping e buscape) mas estabelecer um preço de mercado (atacado e varejo) para uma lista de itens em uma data e a montagem automática de dossiê descritivo e comprobatório deste preço de mercado. 

Ver wiki para documentação

### Dev Install (Linux Ubuntu e Windows):

```
git clone https://github.com/IvanBrasilico/raspa-preco.git
cd raspa-preco
Linux: sudo pip3 install virtualenv (caso ainda não tenha instalado)
Windows: pip install virtualenv (caso ainda não tenha instalado)
python3 -m virtualenv venv
Linux: . venv/bin/activate
Windows: cd venv/Scripts
        activate.bat
pip install -r requirements.txt
pip install -e . # IMPORTANTE para setar . como PYTHONPATH
python raspapreco/restless.py --debug  # Inicia a aplicação
pip install -r dev-requirements.txt
# Testar:
python -m pytest
tox

```
Após iniciar a aplicação, a interface web pode ser acessada em raspapreco/site/ (Preferencialmente publicar o conteúdo deste diretório em um servidor Web)




