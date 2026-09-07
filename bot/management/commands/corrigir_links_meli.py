import re
from django.core.management.base import BaseCommand
from bot.models import Promo
from bot.services import convert_mercado_livre_link


class Command(BaseCommand):
    help = 'Re-converte link_afiliado das promoções do Mercado Livre usando o código corrigido'

    def handle(self, *args, **options):
        corrigidas = 0
        erros = 0
        for promo in Promo.objects.all().order_by('-criado_em'):
            link = promo.link_afiliado or ''
            texto = promo.texto_original or ''

            # Só interessa promos do Mercado Livre
            if not any(s in link for s in ('mercadolivre', 'meli.la', 'mlstatic')):
                continue

            # Procura o link meli.la original no texto (fonte da verdade)
            meli = re.search(r'https?://meli\.la/\S+', texto)
            origem = meli.group(0).rstrip('.,;:!?\'"\u2026)') if meli else link

            novo = convert_mercado_livre_link(origem)
            if not novo or novo == link:
                if not novo:
                    erros += 1
                    self.stdout.write(f'  ! Promo {promo.pk}: falhou ({origem[:60]}...)')
                continue

            promo.link_afiliado = novo
            promo.save(update_fields=['link_afiliado'])
            self.stdout.write(f'Promo {promo.pk}: {link[:70]}')
            self.stdout.write(f'  -> {novo[:110]}')
            corrigidas += 1

        self.stdout.write(self.style.SUCCESS(f'Total corrigidas: {corrigidas}'))
        self.stdout.write(self.style.WARNING(f'Falhas: {erros}'))