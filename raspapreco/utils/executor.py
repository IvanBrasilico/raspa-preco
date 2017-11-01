from datetime import date

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
        Se dossie não fornecido, retorna None
        """
        html = None
        if self.dossie and self.dossie.produtos_encontrados:
            html = '<table><thead><th><tr>'
            for key in self.dossie.produtos_encontrados[0].to_dict():
                html = html + '<td>' + key + '<td>'

            html = html + '</tr></th></thead><tbody>'

            for produtoencontrado in self.dossie.produtos_encontrados:
                html = html + '<tr>'
                for key, value in produtoencontrado.to_dict().items():
                    html = html + '<td>' + str(value) + '<td>'
                html = html + '</tr>'

            html = html + '</tbody></table>'
        return html
