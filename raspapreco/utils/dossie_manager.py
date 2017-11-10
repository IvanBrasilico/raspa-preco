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
    def procedimento(self):
        return self._procedimento

    @property
    def session(self):
        return self._session

    @property
    def scraped(self):
        return self._scraped

    @scraped.setter
    def scraped(self, value):
        self._scraped = value

    @property
    def ultimo_dossie(self):
        if not self._procedimento:
            return None
        return self._procedimento.dossies[
            len(self._procedimento.dossies) - 1]

    def inicia_dossie(self, refazer=False):
        if (not refazer) and (self._dossie is None):
            if self._procedimento.dossies:
                self._dossie = self.ultimo_dossie
        if self._dossie is None:
            self._dossie = Dossie(self._procedimento, datetime.now())
            self._session.add(self._dossie)
            self._session.commit()
        return self._dossie

    def raspa(self, refazer=False):
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
        self.inicia_dossie(refazer)
        # Já houve scrap anterior? Se houve, somente refaz se
        # expressamente comandado
        if refazer or (not self._dossie.produtos_encontrados):
            scrap = Scraper(proc.sites, proc.produtos)
            scrap.scrap()
            self._scraped = scrap.scraped
            return self.monta_dossie()

    def monta_dossie(self):
        """Monta um dossie a partir do resultado de um scrap
        Se procedimento ou session não forem passados, retorna None
        """
        if not self._dossie:
            raise AttributeError('Não há dossiê definido para iniciar')
        if not self._scraped:
            raise AttributeError(
                'Não há raspagem definida para alimentar dossiê')
        session = self._session
        for produto, sites in self._scraped.items():
            produto = session.query(Produto).filter(
                Produto.id == produto).first()
            for site, listas in sites.items():
                site = session.query(Site).filter(
                    Site.id == site).first()
                campos = list(listas.keys())
                descricoes = listas.get('descricao')
                urls = listas.get('url')
                precos = listas.get('preco')
                descricao_site = ''
                url = ''
                preco = None
                for ind in range(len(listas[campos[0]]) - 1):
                    if descricoes:
                        descricao_site = descricoes[ind]
                    if urls:
                        url = urls[ind]
                    if precos:
                        preco = extrai_valor(precos[ind])
                    produtoencontrado = ProdutoEncontrado(
                        self._dossie,
                        produto,
                        site,
                        descricao_site=descricao_site,
                        url=url,
                        preco=preco
                    )
                    camposencontrados = {}
                    for campo in campos:
                        listavaloresdocampo = listas.get(campo)
                        if listavaloresdocampo and \
                                ind < len(listavaloresdocampo):
                            camposencontrados[campo] = listavaloresdocampo[ind]
                    produtoencontrado.campos = camposencontrados
                    session.add(produtoencontrado)
        session.commit()
        return self._dossie

    def dossie_to_html_table(self):
        """Dado um dossiê, retorna seus dados formatados
        Se dossie não fornecido ou vazio, retorna None
        """
        result = None
        if self._dossie and self._dossie.produtos_encontrados:
            result = OrderedDict()
            result['Resumo'] = self.tabelaresumo()

            tablehead = '<table class="table table-striped table-bordered' + \
                ' table-responsive"><thead><tr>'
            tableheadtr = ''
            produtoencontrado = self._dossie.produtos_encontrados[0]
            if produtoencontrado.campos:
                for key, value in produtoencontrado.campos.items():
                    tableheadtr = tableheadtr + '<th>' + key + '</th>'
            else:
                for key in produtoencontrado.to_dict():
                    tableheadtr = tableheadtr + '<th>' + key + '</th>'
            tablehead = tablehead + tableheadtr + '</tr></thead><tbody>'

            for produto in self._dossie.procedimento.produtos:
                html = ''
                q = self._session. \
                    query(ProdutoEncontrado). \
                    filter(ProdutoEncontrado.produto_id == produto.id). \
                    filter(ProdutoEncontrado.dossie_id == self._dossie.id). \
                    all()
                for produtoencontrado in q:
                    html = html + '<tr>'
                    linha = ''
                    if produtoencontrado.campos:
                        for key, value in produtoencontrado.campos.items():
                            value = str(value)
                            linha = linha + '<td'
                            if len(value) > 40:
                                linha = linha + ' data-content="' + value + \
                                    '"' + ' onmouseover=$(this).popover()'
                                value = value[0:40] + '...'
                            linha = linha + '>' + value + '</td>'
                    else:
                        for key, value in produtoencontrado.to_dict().items():
                            value = str(value)
                            linha = linha + '<td'
                            if len(value) > 40:
                                linha = linha + ' data-content="' + value + \
                                    '"' + ' onmouseover=$(this).popover()'
                                value = value[0:40] + '...'
                            linha = linha + '>' + value + '</td>'
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
        if self._dossie and self._dossie.produtos_encontrados:
            tabelaresumo = '<tbody>'

            tablehead = '<table class="table table-striped table-bordered ' + \
                'table-responsive"><thead><tr>' + \
                '<th>Produto</th><th>Valor declarado</th>'
            for site in self._dossie.procedimento.sites:
                tablehead = tablehead + '<th>' + site.title + '</th>'
            tablehead = tablehead + '<th>Média</th><th>%</th>' + \
                '</tr></thead>'

            for produto in self._dossie.procedimento.produtos:
                tabelaresumo += '<tr><td>' + produto.descricao + '</td>'
                tabelaresumo += '<td>' + \
                    '{:0.2f}'.format(produto.preco_declarado) + '</td>'
                for site in self._dossie.procedimento.sites:
                    mediaprodutoporsite = self._session. \
                        query(func.avg(ProdutoEncontrado.preco)). \
                        filter(ProdutoEncontrado.produto_id == produto.id). \
                        filter(ProdutoEncontrado.site_id == site.id). \
                        filter(ProdutoEncontrado.dossie_id ==
                               self._dossie.id).scalar()
                    media = ''
                    if mediaprodutoporsite:
                        media = '{:0.2f}'.format(mediaprodutoporsite)
                    tabelaresumo += '<td>' + media + '</td>'
                mediaproduto = self._session. \
                    query(func.avg(ProdutoEncontrado.preco)). \
                    filter(ProdutoEncontrado.produto_id == produto.id). \
                    filter(ProdutoEncontrado.dossie_id == self._dossie.id). \
                    scalar()
                media = ''
                if mediaproduto:
                    media = '{:0.2f}'.format(mediaproduto)
                else:
                    mediaproduto = 100
                tabelaresumo += '<td>' + media + '</td>'
                tabelaresumo += '<td>' + \
                    '{:0.2f}'.format(produto.preco_declarado /
                                     mediaproduto * 100) + '</td></tr>'
            tabelaresumo += '</tbody></table>'
            tabelaresumo = tablehead + tabelaresumo
        return tabelaresumo
