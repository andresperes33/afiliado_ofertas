with open('bot/templates/bot/base.html', 'r', encoding='utf-8') as f:
    content = f.read()
old = '                <a href="#" class="mobile-link" id="btnAppQrMobile"><i class="fas fa-mobile-alt"></i> Baixar o app</a>\n                <a href="/promos/" class="mobile-link {% block nav_promos_mobile %}active{% endblock %}"><i class="fas fa-store"></i> Promoções</a>\n                <a href="{% url \'nitroalerta\' %}" class="mobile-link"><i class="fas fa-bell"></i> Nitro Alerta</a>\n                <a href="{% url \'sobre\' %}" class="mobile-link"><i class="fas fa-info-circle"></i> Sobre</a>\n                <a href="{% url \'contato\' %}" class="mobile-link"><i class="fas fa-envelope"></i> Contato</a>'
new = '                <a href="#" class="mobile-link" id="btnAppQrMobile"><i class="fas fa-mobile-alt"></i> Baixar app</a>'
content = content.replace(old, new)
with open('bot/templates/bot/base.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('mobile ok')
