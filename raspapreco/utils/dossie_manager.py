from collections import OrderedDict
from datetime import datetime

from sqlalchemy import func

from raspapreco.models.models import Dossie, Produto, ProdutoEncontrado, Site
from raspapreco.utils.site_scraper import Scraper, extrai_valor


class DossieManager():
    """Executa scrap a partir de um procedimento, montando um dossie
    Dado um dossiê, retorna seus dados formatados
    """

    def __init__(self, session, procedimento=None, dossie=None):
        self._procedimento = procedimento
        self._session = session
        self._dossie = dossie
        self._scraped = None

    @property
    def dossie(self):
        return self._dossie

    @property
    def procedimento(self):
        return self._procedimento

    @property
    def session(self):
        return self._session

    @property
    def ultimo_dossie(self):
        if not self._procedimento:
            return None
        return self._procedimento.dossies[
            len(self._procedimento.dossies) - 1]

    def inicia_dossie(self, task_id=None):
        if self._dossie is None:
            if self._procedimento.dossies:
                self._dossie = self.ultimo_dossie
        if self._dossie is None:
            self._dossie = Dossie(self._procedimento, datetime.now())
            self._dossie.task_id = task_id
            self._session.add(self._dossie)
            self._session.commit()
        return self._dossie

    def raspa(self, scraped=None):
        """Executa scrap a partir de um procedimento
        Os dados da raspagem iniciarão os dados de um dossie
        Se procedimento ou session não forem passados, retorna None
        """
        session = self._session
        if session is None:
            return None
        proc = self._procedimento
        if proc is None:
            return None
        self.inicia_dossie()
        if scraped:
            self._scraped = scraped
        else:
            scrap = Scraper(proc.sites, proc.produtos)
            scrap.scrap()
            self._scraped = scrap.scraped
        self.monta_dossie()

    def monta_dossie(self):
        """Monta um dossie a partir do resultado de um scrap
        Se procedimento ou session não forem passados, retorna None
        """
        if not self._dossie:
            raise AttributeError('Não há dossiê definido para iniciar')
        session = self._session
        for produto, sites in self._scraped.items():
            produto = session.query(Produto).filter(
                Produto.id == produto).first()
            for site, campos in sites.items():
                site = session.query(Site).filter(
                    Site.id == site).first()
                for ind in range(len(campos['url'])):
                    produtoencontrado = ProdutoEncontrado(
                        self._dossie,
                        produto,
                        site,
                        descricao_site=campos['descricao'][ind],
                        url=campos['url'][ind],
                        preco=extrai_valor(campos['preco'][ind])
                    )
                    session.add(produtoencontrado)
        session.commit()
        return self._dossie

    def dossie_to_html_table(self):
        """Dado um dossiê, retorna seus dados formatados
        Se dossie não fornecido ou vazio, retorna None
        """
        result = None
        if self.dossie and self.dossie.produtos_encontrados:
            result = OrderedDict()
            result['Resumo'] = self.tabelaresumo()

            tablehead = '<table class="table table-striped table-bordered' + \
                ' table-responsive"><thead><tr>'
            tableheadtr = ''
            for key in self.dossie.produtos_encontrados[0].to_dict():
                tableheadtr = tableheadtr + '<th>' + key + '</th>'
            tablehead = tablehead + tableheadtr + '</tr></thead><tbody>'

            for produto in self.dossie.procedimento.produtos:
                html = ''
                q = self._session. \
                    query(ProdutoEncontrado). \
                    filter(ProdutoEncontrado.produto_id == produto.id). \
                    filter(ProdutoEncontrado.dossie_id == self.dossie.id). \
                    all()
                for produtoencontrado in q:
                    html = html + '<tr>'
                    linha = ''
                    for key, value in produtoencontrado.to_dict().items():
                        linha = linha + '<td>' + str(value) + '</td>'
                    html = html + linha + '</tr>'
                html = tablehead + html + '</tbody></table>'
                result[produto.descricao] = html

        return result

    def tabelaresumo(self):
        """Dado um dossiê, retorna tabela resumo de preços dos
        produtos encontrados por site.
        Se dossie não fornecido ou vazio, retorna None
        """
        tabelaresumo = None
        if self.dossie and self.dossie.produtos_encontrados:
            tabelaresumo = '<tbody>'

            tablehead = '<table class="table table-striped table-bordered ' + \
                'table-responsive"><thead><tr>' + \
                '<th>Produto</th><th>Valor declarado</th>'
            for site in self.dossie.procedimento.sites:
                tablehead = tablehead + '<th>' + site.title + '</th>'
            tablehead = tablehead + '<th>Média</th><th>%</th>' + \
                '</tr></thead>'

            for produto in self.dossie.procedimento.produtos:
                tabelaresumo += '<tr><td>' + produto.descricao + '</td>'
                tabelaresumo += '<td>' + \
                    '{:0.2f}'.format(produto.preco_declarado) + '</td>'
                for site in self.dossie.procedimento.sites:
                    totalprodutoporsite = self._session. \
                        query(func.avg(ProdutoEncontrado.preco)). \
                        filter(ProdutoEncontrado.produto_id == produto.id). \
                        filter(ProdutoEncontrado.site_id == site.id). \
                        filter(ProdutoEncontrado.dossie_id ==
                               self.dossie.id).scalar()
                    tabelaresumo += '<td>' + \
                        '{:0.2f}'.format(totalprodutoporsite) + '</td>'
                mediaproduto = self._session. \
                    query(func.avg(ProdutoEncontrado.preco)). \
                    filter(ProdutoEncontrado.produto_id == produto.id). \
                    filter(ProdutoEncontrado.dossie_id == self.dossie.id). \
                    scalar()
                tabelaresumo += '<td>' + \
                    '{:0.2f}'.format(mediaproduto) + '</td>'
                tabelaresumo += '<td>' + \
                    '{:0.2f}'.format(produto.preco_declarado /
                                     mediaproduto * 100) + '</td></tr>'
            tabelaresumo += '</tbody></table>'
            tabelaresumo = tablehead + tabelaresumo
        return tabelaresumo
