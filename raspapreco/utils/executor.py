from datetime import date

from sqlalchemy import func

from raspapreco.models.models import Dossie, Produto, ProdutoEncontrado, Site
from raspapreco.utils.site_scraper import Scraper, extrai_valor


class Executor():
    """Executa scrap a partir de um procedimento, montando um dossie
    Dado um dossiê, retorna seus dados formatados
    """

    def __init__(self, session, procedimento=None, dossie=None):
        self._procedimento = procedimento
        self._session = session
        self._dossie = dossie

    def scrap(self):
        """Executa scrap a partir de um procedimento, montando um dossie
        Se procedimento ou session não forem passados, retorna None
        """
        session = self._session
        if session is None:
            return None
        proc = self._procedimento
        if proc is None:
            return None
        scrap = Scraper(proc.sites, proc.produtos)
        scrap.scrap()
        dossie = Dossie(self._procedimento, date.today())
        session.add(dossie)
        session.commit()
        for produto, sites in scrap.scraped.items():
            produto = session.query(Produto).filter(
                Produto.id == produto).first()
            for site, campos in sites.items():
                site = session.query(Site).filter(
                    Site.id == site).first()
                for ind in range(len(campos['url'])):
                    produtoencontrado = ProdutoEncontrado(
                        dossie,
                        produto,
                        site,
                        descricao_site=campos['descricao'][ind],
                        url=campos['url'][ind],
                        preco=extrai_valor(campos['preco'][ind])
                    )
                    session.add(produtoencontrado)
        session.commit()
        self._dossie = dossie
        return self._dossie

    @property
    def dossie(self):
        return self._dossie

    def dossie_to_html_table(self):
        """Dado um dossiê, retorna seus dados formatados
        Se dossie não fornecido ou vazio, retorna None
        """
        html = None
        if self.dossie and self.dossie.produtos_encontrados:
            html = self.tabelaresumo()

            tablehead = '<table><thead><th><tr>'
            for key in self.dossie.produtos_encontrados[0].to_dict():
                tablehead = tablehead + '<td>' + key + '<td>'
            tablehead = tablehead + '</tr></th></thead>'

            for produto in self.dossie.procedimento.produtos:
                html = html + '<hr>&nbsp;'
                html = html + '<h3>' + produto.descricao + '<h3>'
                html = html + tablehead + '<tbody>'
                q = self._session. \
                    query(ProdutoEncontrado). \
                    filter(ProdutoEncontrado.produto_id == produto.id). \
                    filter(ProdutoEncontrado.dossie_id == self.dossie.id). \
                    all()
                for produtoencontrado in q:
                    html = html + '<tr>'
                    for key, value in produtoencontrado.to_dict().items():
                        html = html + '<td>' + str(value) + '<td>'
                    html = html + '</tr>'
                html = html + '</tbody></table>'

        return html

    def tabelaresumo(self):
        """Dado um dossiê, retorna tabela resumo de preços dos
        produtos encontrados por site.
        Se dossie não fornecido ou vazio, retorna None
        """
        tabelaresumo = None
        if self.dossie and self.dossie.produtos_encontrados:
            tabelaresumo = '<tbody>'

            tablehead = '<table><thead><th><tr><td>-</td>'
            for site in self.dossie.procedimento.sites:
                tablehead = tablehead + '<td>' + site.title + '<td>'
            tablehead = tablehead + '<td>Total</td></tr></th></thead>'

            for produto in self.dossie.procedimento.produtos:
                tabelaresumo += '<tr><td>' + produto.descricao + '</td>'
                for site in self.dossie.procedimento.sites:
                    totalprodutoporsite = self._session. \
                        query(func.avg(ProdutoEncontrado.preco)). \
                        filter(ProdutoEncontrado.produto_id == produto.id). \
                        filter(ProdutoEncontrado.site_id == site.id). \
                        filter(ProdutoEncontrado.dossie_id ==
                               self.dossie.id).scalar()
                    tabelaresumo += '<td>' + str(totalprodutoporsite) + '<td>'
                totalproduto = self._session. \
                    query(func.avg(ProdutoEncontrado.preco)). \
                    filter(ProdutoEncontrado.produto_id == produto.id). \
                    filter(ProdutoEncontrado.dossie_id == self.dossie.id). \
                    scalar()
                tabelaresumo += '<td>' + str(totalproduto) + '</td></tr>'
            tabelaresumo += '</tbody></table>'
            tabelaresumo = tablehead + tabelaresumo
        return tabelaresumo
