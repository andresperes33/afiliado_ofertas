import logging
import os
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

GRAPH_URL = "https://graph.facebook.com/v26.0"


def _mensagem_post(texto, pagina_url=''):
    """Monta a mensagem do post: título + preço + link da oferta no site."""
    # Ignora a 1ª linha (banner/gancho do anúncio): o título real do
    # produto sempre fica a partir da 2ª linha.
    linhas = (texto or '').split('\n')
    a_partir_segunda = '\n'.join(linhas[1:]) if len(linhas) > 1 else (texto or '')

    try:
        from bot.services import _linha_titulo, _preco_do_texto
        titulo = _linha_titulo(a_partir_segunda)[:150]
        preco = _preco_do_texto(texto)
    except Exception:
        titulo = ''
        preco = ''

    mensagem = (titulo or a_partir_segunda or '').strip()
    if not mensagem:
        mensagem = "Oferta imperdível"
    if preco:
        mensagem += f"\n{preco}"
    if pagina_url:
        mensagem += f"\n\n{pagina_url}"
    return mensagem.strip()


def post_facebook(texto, photo_path=None, pagina_url=''):
    """
    Publica a oferta na página do Facebook (Página Nitro Ofertas - Achadinhos).

    Com foto: publica a imagem + mensagem (upload direto).
    Sem foto: publica post de texto + link.
    """
    token = getattr(settings, 'FB_ACCESS_TOKEN', None)
    page_id = getattr(settings, 'FB_PAGE_ID', None)
    if not token or not page_id:
        logger.warning("⚠️ Facebook não configurado (FB_ACCESS_TOKEN / FB_PAGE_ID).")
        return False

    mensagem = _mensagem_post(texto, pagina_url)

    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, 'rb') as foto:
                resp = requests.post(
                    f"{GRAPH_URL}/{page_id}/photos",
                    files={'source': foto},
                    data={'message': mensagem, 'access_token': token},
                    timeout=60,
                )
        else:
            resp = requests.post(
                f"{GRAPH_URL}/{page_id}/feed",
                data={'message': mensagem, 'access_token': token},
                timeout=60,
            )
        data = resp.json()
    except Exception as e:
        logger.error(f"❌ Facebook: erro ao publicar: {e}")
        return False

    if resp.status_code not in (200, 201) or 'id' not in data:
        logger.error(f"❌ Facebook: falha ao publicar: {data}")
        return False

    logger.info(f"✅ Post publicado no Facebook: {data.get('id')}")
    return True