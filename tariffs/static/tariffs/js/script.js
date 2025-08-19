document.addEventListener('DOMContentLoaded', function() {
    // Элементы DOM
    const tariffCards = document.querySelectorAll(".tariff-card");
    const filterButtons = document.querySelectorAll(".filter-btn");
    const form = document.getElementById('lead-form');
    const status = document.getElementById('lead-status');
    const phoneInput = document.getElementById('phone');

    // Маска для телефона
    phoneInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.startsWith('7') || value.startsWith('8')) {
            value = value.substring(1);
        }
        if (value.length > 0) {
            value = '+7 (' + value;
            if (value.length > 7) value = value.substring(0, 7) + ') ' + value.substring(7);
            if (value.length > 12) value = value.substring(0, 12) + '-' + value.substring(12);
            if (value.length > 15) value = value.substring(0, 15) + '-' + value.substring(15);
        }
        e.target.value = value;
    });

    // Логика для поддоменов
    function updateRegionUI() {
        const regionName = document.querySelector('.current-region').textContent;

        // Обновляем текст в форме
        document.getElementById('region-input').value = regionName;

        // Поддомен уже фильтрует тарифы на сервере, просто показываем все видимые
        tariffCards.forEach(card => {
            card.style.display = 'block';
        });
    }

    // Фильтрация по скорости
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const speedFilter = this.dataset.speed;
            filterBySpeed(speedFilter);
        });
    });

    function filterBySpeed(speedFilter) {
        tariffCards.forEach(card => {
            const cardSpeed = parseInt(card.dataset.speed) || 0;
            const matchesSpeed = !speedFilter || cardSpeed <= parseInt(speedFilter);
            card.style.display = matchesSpeed ? "block" : "none";
        });
    }

    // Обработчик для переключения регионов через dropdown
    document.querySelectorAll('.dropdown-content a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = this.href;
        });
    });

    // Автозаполнение тарифа при клике на кнопку
    document.querySelectorAll('.tariff-card .btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tariffId = this.dataset.tariff;
            document.getElementById('tariff-select').value = tariffId;

            // Плавная прокрутка к форме
            document.getElementById('connect-form').scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Обработка формы
    form.addEventListener('submit', async e => {
        e.preventDefault();

        // Валидация
        const fio = document.getElementById('fio').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const address = document.getElementById('address').value.trim();
        const tariff = document.getElementById('tariff-select').value;

        if (!fio || !phone || !address || !tariff) {
            showStatus('Заполните все обязательные поля', 'error');
            return;
        }

        if (phone.replace(/\D/g, '').length !== 11) {
            showStatus('Введите корректный номер телефона', 'error');
            return;
        }

        form.classList.add('loading');
        status.style.display = 'block';
        status.textContent = 'Заявка отправляется…';

        const formData = Object.fromEntries(new FormData(form).entries());

        try {
            const res = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formData)
            });

            const data = await res.json();

            if (!res.ok) throw new Error(data.error || 'Ошибка сервера');

            showStatus('Спасибо! Мы свяжемся с вами в течение 15 минут.', 'success');
            form.reset();

        } catch (error) {
            showStatus(error.message || 'Не удалось отправить заявку. Попробуйте позже.', 'error');
        } finally {
            form.classList.remove('loading');
        }
    });

    // Вспомогательные функции
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    function showStatus(message, type) {
        status.textContent = message;
        status.className = type === 'success' ? 'success-message' : 'error-message';
        status.style.display = 'block';

        // Автоскрытие успешного сообщения
        if (type === 'success') {
            setTimeout(() => {
                status.style.display = 'none';
            }, 5000);
        }
    }

    // Анимации при скролле
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.fade-in').forEach(el => {
        observer.observe(el);
    });

    // Инициализация
    updateRegionUI();
});