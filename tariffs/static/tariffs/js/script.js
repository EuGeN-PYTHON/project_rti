document.addEventListener('DOMContentLoaded', function() {
    // Элементы DOM
    const filterButtons = document.querySelectorAll(".filter-btn");
    const form = document.getElementById('lead-form');
    const status = document.getElementById('lead-status');
    const phoneInput = document.getElementById('phone');
    const regionDropdown = document.querySelector('.region-dropdown');
    const dropdownContent = document.querySelector('.dropdown-content');

    // Настройка dropdown
    function setupDropdown() {
        if (!regionDropdown || !dropdownContent) return;
        let dropdownTimeout;

        regionDropdown.addEventListener('mouseenter', function() {
            clearTimeout(dropdownTimeout);
            dropdownContent.style.display = 'block';
            setTimeout(() => {
                dropdownContent.style.opacity = '1';
                dropdownContent.style.transform = 'translateY(0)';
            }, 10);
        });

        regionDropdown.addEventListener('mouseleave', function() {
            dropdownTimeout = setTimeout(() => {
                dropdownContent.style.opacity = '0';
                dropdownContent.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    dropdownContent.style.display = 'none';
                }, 300);
            }, 300);
        });

        dropdownContent.addEventListener('mouseenter', function() {
            clearTimeout(dropdownTimeout);
        });

        dropdownContent.addEventListener('mouseleave', function() {
            dropdownContent.style.opacity = '0';
            dropdownContent.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                dropdownContent.style.display = 'none';
            }, 300);
        });
    }

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

    // Фильтрация по пакетам услуг
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            const filterType = this.dataset.filter;
            filterByPackage(filterType);
        });
    });

    function filterByPackage(filterType) {
        const rtCarouselItems = document.querySelectorAll('.rt-carousel-item');

        let visibleCount = 0;
        rtCarouselItems.forEach(item => {
            const hasTV = item.querySelector('.Basic_channel_packages.enabled') !== null;
            const hasCinema = item.querySelector('.ONLINE_CINEMA.enabled') !== null;
            const hasMobile = item.querySelector('.SIM-card_main.enabled') !== null;

            let matchesFilter = false;

            switch(filterType) {
                case 'all':
                    matchesFilter = true;
                    break;
                case 'tv_cinema':
                    matchesFilter = hasTV && hasCinema;
                    break;
                case 'mobile':
                    matchesFilter = hasMobile;
                    break;
                case 'all_services':
                    matchesFilter = hasTV && hasCinema && hasMobile;
                    break;
                default:
                    matchesFilter = true;
            }

            item.style.display = matchesFilter ? "block" : "none";
            if (matchesFilter) visibleCount++;
        });

        // Переинициализируем карусель после фильтрации
        setTimeout(initCarousel, 100);
    }

    // Обработка кнопок подключения
    document.querySelectorAll('.rt-button-orange').forEach(btn => {
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
            showStatus('Пожалуйста, заполните все поля', 'error');
            return;
        }

        if (phone.replace(/\D/g, '').length < 11) {
            showStatus('Введите корректный номер телефона', 'error');
            return;
        }

        // Имитация отправки
        showStatus('Отправляем заявку...', 'loading');

        try {
            // Здесь будет реальный запрос к API
            await new Promise(resolve => setTimeout(resolve, 2000));

            showStatus('Заявка успешно отправлена! Мы свяжемся с вами в течение 15 минут', 'success');
            form.reset();

        } catch (error) {
            showStatus('Ошибка при отправке. Попробуйте еще раз', 'error');
        }
    });

    function showStatus(message, type) {
        status.textContent = message;
        status.className = type === 'success' ? 'success-message' :
                          type === 'error' ? 'error-message' :
                          'loading-message';
        status.style.display = 'block';

        if (type === 'success' || type === 'error') {
            setTimeout(() => {
                status.style.display = 'none';
            }, 5000);
        }
    }

    // FAQ Accordion functionality
    function initFAQ() {
        const faqItems = document.querySelectorAll('.faq-item');

        if (faqItems.length === 0) return; // Если элементов нет, выходим

        faqItems.forEach(item => {
            const question = item.querySelector('.faq-question');

            question.addEventListener('click', () => {
                // Закрываем все открытые вопросы
                faqItems.forEach(otherItem => {
                    if (otherItem !== item && otherItem.classList.contains('active')) {
                        otherItem.classList.remove('active');
                    }
                });

                // Переключаем текущий вопрос
                item.classList.toggle('active');
            });
        });
    }

    // Инициализация всех компонентов
    setupDropdown();
    initCarousel();
    initFAQ();
    filterByPackage('all'); // Инициализация фильтров

    // Анимации при скролле
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Наблюдаем за элементами для анимации (добавлен .faq-item)
    document.querySelectorAll('.feature-card, .rt-tariff-card, .lead-card, .faq-item').forEach(el => {
        observer.observe(el);
    });
});