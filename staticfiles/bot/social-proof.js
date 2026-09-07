(function () {
    var NAMES = [
        'João', 'Pedro', 'Lucas', 'Mateus', 'Rafael', 'Bruno', 'Gustavo',
        'Felipe', 'Thiago', 'Ricardo', 'Marcelo', 'Anderson', 'Carlos',
        'Eduardo', 'Fernando', 'Paulo', 'Rodrigo', 'Diego', 'Leonardo',
        'Rafaela', 'Juliana', 'Camila', 'Patrícia', 'Amanda', 'Bruna',
        'Carla', 'Fernanda', 'Letícia', 'Vanessa', 'Priscila'
    ];
    var CITIES = [
        'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba',
        'Porto Alegre', 'Salvador', 'Recife', 'Fortaleza', 'Brasília',
        'Goiânia', 'Florianópolis', 'Campinas', 'Manaus', 'Belém'
    ];
    var PRODUCTS = [
        { icon: 'fa-shirt', text: 'Camiseta Básica Algodão' },
        { icon: 'fa-shirt', text: 'Calça Jeans Feminina' },
        { icon: 'fa-shirt', text: 'Vestido Midi Floral' },
        { icon: 'fa-shoe-prints', text: 'Tênis Casual Masculino' },
        { icon: 'fa-shoe-prints', text: 'Tênis Feminino Esportivo' },
        { icon: 'fa-bag-shopping', text: 'Mochila Executiva' },
        { icon: 'fa-bag-shopping', text: 'Bolsa Feminina Couro' },
        { icon: 'fa-person', text: 'Jaqueta Corta-Vento' },
        { icon: 'fa-person', text: 'Calça Legging Fitness' },
        { icon: 'fa-person', text: 'Bermuda Masculina Sarja' },
        { icon: 'fa-socks', text: 'Kit Meias Cano Alto' },
        { icon: 'fa-wrench', text: 'Furadeira de Impacto' },
        { icon: 'fa-hammer', text: 'Kit Chaves de Fenda' },
        { icon: 'fa-screwdriver-wrench', text: 'Parafusadeira sem Fio' },
        { icon: 'fa-gears', text: 'Jogo de Soquetes 14 peças' },
        { icon: 'fa-toolbox', text: 'Caixa de Ferramentas 169 peças' },
        { icon: 'fa-utensils', text: 'Jogo de Panelas Antiaderente' },
        { icon: 'fa-kitchen-set', text: 'Frigideira Cerâmica 24cm' },
        { icon: 'fa-mug-hot', text: 'Liquidificador 600W' },
        { icon: 'fa-blender', text: 'Air Fryer 5L' },
        { icon: 'fa-couch', text: 'Cortina Blackout 200x180' },
        { icon: 'fa-bed', text: 'Jogo de Lençol Queen' },
        { icon: 'fa-bath', text: 'Kit Toalhas de Banho' },
        { icon: 'fa-box-open', text: 'Organizador de Cozinha' },
        { icon: 'fa-dumbbell', text: 'Kit Halteres 10kg' },
        { icon: 'fa-bottle-water', text: 'Garrafa Térmica Inox 1L' },
        { icon: 'fa-baby', text: 'Kit 10 Marmitas Herméticas' },
        { icon: 'fa-couch', text: 'Tapete de Banheiro Antiderrapante' },
        { icon: 'fa-tshirt', text: 'Kit 7 Camisetas Masculinas' },
        { icon: 'fa-vest', text: 'Jaqueta Puffer Impermeável' },
        { icon: 'fa-shoe-prints', text: 'Chinelo Conforto Masculino' },
        { icon: 'fa-shirt', text: 'Kit 3 Bermudas Masculinas' },
        { icon: 'fa-toolbox', text: 'Alicate de Pressão 10"' },
        { icon: 'fa-hammer', text: 'Kit 32 Chaves Hexagonais' },
        { icon: 'fa-paint-roller', text: 'Broca de Vídea 10 peças' }
    ];
    var TIMES = [
        'há 2 minutos', 'há 5 minutos', 'há 8 minutos', 'há 12 minutos',
        'há 15 minutos', 'há 20 minutos', 'há 3 minutos', 'há 7 minutos',
        'há 1 minuto', 'há 10 minutos'
    ];

    function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

    function buildMessage() {
        var name = pick(NAMES);
        var city = pick(CITIES);
        var product = pick(PRODUCTS);
        var time = pick(TIMES);
        return {
            icon: product.icon,
            html: '<strong>' + name + '</strong> de ' + city + ' <br>comprou <strong>' + product.text + '</strong>',
            time: time
        };
    }

    var el = document.getElementById('socialProof');
    if (!el) return;

    var iconEl = el.querySelector('.social-proof-icon i');
    var textEl = el.querySelector('.social-proof-text');
    var timeEl = el.querySelector('.social-proof-time');
    var closeBtn = el.querySelector('.social-proof-close');
    var timer = null;
    var interval = null;

    function showNotification() {
        var msg = buildMessage();
        iconEl.className = 'fas ' + msg.icon;
        textEl.innerHTML = msg.html;
        timeEl.textContent = msg.time;
        el.classList.add('show');
        timer = setTimeout(hideNotification, 5000);
    }

    function hideNotification() {
        if (timer) { clearTimeout(timer); timer = null; }
        el.classList.remove('show');
    }

    function startCycle() {
        showNotification();
        interval = setInterval(function () {
            hideNotification();
            setTimeout(showNotification, 600);
        }, 12000);
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            hideNotification();
            if (interval) { clearInterval(interval); interval = null; }
        });
    }

    setTimeout(startCycle, 3000);
})();
