.. Raspa Preço documentation master file, created by
   sphinx-quickstart on Mon Nov  6 10:52:29 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Raspa Preço's documentation!
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Este projeto serve para "raspar" sites e montar dossiês. Por exemplo,
para fazer pesquisa de preço declarado de produto em uma licitação,
uma operação ou uma operação. 

[Histórias de usuário](https://github.com/IvanBrasilico/raspa-preco/wiki/UserStories)

[Projeto](https://github.com/IvanBrasilico/raspa-preco/)

As instruções de instalação estão no arquivo README e mais detalhadamente no
arquivo shell-commands-history.

Os módulos de teste mostram o funcionamento do Sistema.

Como exemplo rápido de funcionalidade, ver o código dos 
scripts raspapreco/tests/ raspa_site_dinamico.py e site_scrapper_hot_test.py

**raspa_site_dinamico.py**

.. literalinclude:: raspapreco/tests/raspa_site_dinamico.py
    :language: python3
    :linenos:
    :lines: 13-36

**site_scrapper_hot_test.py**

.. literalinclude:: raspapreco/tests/site_scrapper_hot_test.py
    :language: python3
    :linenos:
    :lines: 46-71

.. automodule:: raspapreco.utils.site_scraper
    :members:

.. automodule:: raspapreco.utils.dossie_manager
    :members:

.. automodule:: raspapreco.models.models
    :members:

.. automodule:: raspapreco.app
    :members:

.. automodule:: raspapreco.restless
    :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
