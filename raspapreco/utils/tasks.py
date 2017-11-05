from celery import Celery

from raspapreco.models.models import Base, MySession, Procedimento
from raspapreco.utils.dossie_manager import DossieManager

mysession = MySession(Base)
session = mysession.session()

celery = Celery('raspapreco.utils.tasks', broker='pyamqp://guest@localhost//',
                backend='rpc://')


@celery.task(bind=True)
def raspac(self, procedimento):
    """Background task that runs a long function with progress reports."""
    """
    https://blog.miguelgrinberg.com/post/using-celery-with-flask
    """
    proc = session.query(Procedimento).filter(
        Procedimento.id == procedimento).first()
    dossiemanager = DossieManager(session, proc)

    dossiemanager.raspa()
    return {'result': dossiemanager.dossie_to_html_table()}
