from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Promo

_LOJAS_FIXAS = [
    'Shopee', 'Amazon', 'AliExpress', 'Mercado Livre', 'KaBuM',
    'Magazine Luíza', 'Pichau', 'Terabyte', 'Americanas', 'Casas Bahia',
]


def promo_detail_view(request, pk):
    import re
    from bot.services import _RODAPE_CANAIS_HTML
    promo = get_object_or_404(Promo, pk=pk)
    recentes = Promo.objects.exclude(pk=pk)[:3]

    historico = []
    chart_data = []

    def _normalizar_preco(p):
        m = re.search(r'R\$\s*(\d[\d.,]*)', p or '')
        if not m:
            return None
        v = m.group(1).replace('.', '').replace(',', '.')
        try:
            return round(float(v), 2)
        except ValueError:
            return None

    if promo.produto_chave:
        linhas = list(
            Promo.objects
            .filter(produto_chave=promo.produto_chave)
            .exclude(preco='')
            .order_by('criado_em')
            .values('preco', 'criado_em', 'pk', 'loja', 'link_afiliado')
        )
        if promo.preco:
            linhas.append({
                'preco': promo.preco, 'criado_em': promo.criado_em,
                'pk': promo.pk, 'loja': promo.loja, 'link_afiliado': promo.link_afiliado,
            })

        por_valor = {}
        for item in linhas:
            v = _normalizar_preco(item['preco'])
            if v is None:
                continue
            por_valor[v] = item

        for item in sorted(por_valor.values(), key=lambda it: it['criado_em']):
            historico.append(item)
            chart_data.append({
                'data': item['criado_em'].isoformat(),
                'valor': _normalizar_preco(item['preco']),
            })

    return render(request, 'bot/promo_detail.html', {
        'promo': promo,
        'recentes': recentes,
        'historico': historico,
        'chart_data': chart_data,
        'rodape_canais': _RODAPE_CANAIS_HTML,
    })


def promos_view(request):
    LIMITE = 12
    promos = Promo.objects.all()

    periodo = request.GET.get('periodo', 'hoje')
    agora = timezone.localtime(timezone.now())
    if periodo == 'hoje':
        promos = promos.filter(criado_em__date=agora.date())
    elif periodo == 'semana':
        promos = promos.filter(criado_em__gte=agora - timedelta(days=7))
    elif periodo == 'mes':
        promos = promos.filter(criado_em__gte=agora - timedelta(days=30))

    lojas_bd = list(promos.exclude(loja='').order_by('loja').values_list('loja', flat=True).distinct())
    lojas = list(_LOJAS_FIXAS) + [l for l in lojas_bd if l not in _LOJAS_FIXAS]

    loja = request.GET.get('loja', '')
    if loja:
        promos = promos.filter(loja=loja)

    q = request.GET.get('q', '')
    if q:
        promos = promos.filter(titulo__icontains=q) | Promo.objects.filter(texto_original__icontains=q)

    promos = promos.order_by('-criado_em')
    total = promos.count()

    try:
        offset = max(int(request.GET.get('offset', '0')), 0)
    except (TypeError, ValueError):
        offset = 0

    busca_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' and bool(request.GET.get('offset'))
    pagina = promos[offset:offset + LIMITE]
    tem_mais = total > (offset + len(pagina))

    if busca_ajax:
        return render(request, 'bot/_promo_grid_page.html', {
            'promos': pagina,
            'offset': offset,
            'tem_mais': tem_mais,
            'total': total,
        })

    return render(request, 'bot/promos.html', {
        'promos': pagina,
        'periodo': periodo,
        'lojas': lojas,
        'loja_ativa': loja,
        'q': q,
        'total': total,
        'offset': offset,
        'tem_mais': tem_mais,
        'LIMITE': LIMITE,
    })


def privacy_view(request):
    return render(request, 'bot/privacy.html')


def sobre_view(request):
    return render(request, 'bot/sobre.html')


def contato_view(request):
    return render(request, 'bot/contato.html')


def termos_view(request):
    return render(request, 'bot/termos.html')


def nitroalerta_view(request):
    from .models import AlertaSite
    from .services import normalizar_whatsapp

    sucesso = None
    erro = None

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        numero = request.POST.get('whatsapp', '').strip()
        keyword = request.POST.get('keyword', '').strip()

        if not nome:
            erro = 'Digite seu nome.'
        elif not numero:
            erro = 'Digite seu número de WhatsApp (DDD + número).'
        elif not keyword:
            erro = 'Digite qual produto você quer acompanhar.'
        else:
            wa = normalizar_whatsapp(numero)
            if len(wa) < 13:
                erro = 'Número inválido. Digite no formato: 38 999821883 (DDD + número).'
            else:
                import secrets
                AlertaSite.objects.create(
                    nome=nome,
                    whatsapp=wa,
                    keyword=keyword,
                    token=secrets.token_urlsafe(32),
                )
                sucesso = f'Pronto, {nome} ! Vamos te avisar quando aparecer oferta de "{keyword}".'

    return render(request, 'bot/nitroalerta.html', {'sucesso': sucesso, 'erro': erro})


def nitroalerta_cancelar_view(request, token):
    from .models import AlertaSite

    alerta = AlertaSite.objects.filter(token=token).first()
    if not alerta:
        return render(request, 'bot/nitroalerta_cancelar.html', {'ok': False, 'ja_inativo': False})

    if not alerta.is_active:
        return render(request, 'bot/nitroalerta_cancelar.html', {'ok': False, 'ja_inativo': True})

    alerta.is_active = False
    alerta.save(update_fields=['is_active'])
    return render(request, 'bot/nitroalerta_cancelar.html', {'ok': True, 'ja_inativo': False})


def robots_txt_view(request):
    base_url = request.build_absolute_uri('/').rstrip('/')
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "",
        f"Sitemap: {base_url}/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def ads_txt_view(request):
    from django.http import HttpResponse
    lines = [
        "google.com, pub-1945676049008537, DIRECT, f08c47fec0942fa0",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml_view(request):
    from django.http import HttpResponse
    base_url = request.build_absolute_uri('/').rstrip('/')
    pages = [
        {"loc": f"{base_url}/promos/", "changefreq": "always", "priority": "1.0"},
        {"loc": f"{base_url}/nitro-alerta/", "changefreq": "monthly", "priority": "0.5"},
        {"loc": f"{base_url}/sobre/", "changefreq": "monthly", "priority": "0.3"},
        {"loc": f"{base_url}/contato/", "changefreq": "monthly", "priority": "0.3"},
        {"loc": f"{base_url}/termos-de-uso/", "changefreq": "monthly", "priority": "0.3"},
        {"loc": f"{base_url}/politica-de-privacidade/", "changefreq": "monthly", "priority": "0.3"},
    ]

    for promo in Promo.objects.all()[:500]:
        pages.append({
            "loc": f"{base_url}/promos/{promo.pk}/",
            "changefreq": "weekly",
            "priority": "0.8",
        })

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for p in pages:
        xml.append('  <url>')
        xml.append(f'    <loc>{p["loc"]}</loc>')
        xml.append(f'    <changefreq>{p["changefreq"]}</changefreq>')
        xml.append(f'    <priority>{p["priority"]}</priority>')
        xml.append('  </url>')
    xml.append('</urlset>')

    return HttpResponse("\n".join(xml), content_type="application/xml")
