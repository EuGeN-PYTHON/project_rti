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
            const hasInternet = item.querySelector('.Main_Internet_service.enabled') !== null;

            let matchesFilter = false;

            switch(filterType) {
                case 'all':
                    matchesFilter = true;
                    break;
                case 'internet': // Только домашний интернет
                    matchesFilter = hasInternet && !hasTV && !hasCinema && !hasMobile;
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

    // Функция инициализации карусели
    function initCarousel() {
        const carousel = document.getElementById('rt-tariff-carousel');
        if (!carousel) return;

        const items = carousel.querySelectorAll('.rt-carousel-item');
        const prevBtn = document.querySelector('.rt-carousel-prev');
        const nextBtn = document.querySelector('.rt-carousel-next');
        const dotsContainer = document.querySelector('.rt-carousel-dots');
        const wrapper = document.querySelector('.rt-carousel-wrapper');

        if (items.length === 0) return;

        let currentIndex = 0;
        let itemsPerView = 3;
        let totalSlides = Math.ceil(items.length / itemsPerView);
        let isAnimating = false;

        // Определяем количество видимых элементов
        function updateItemsPerView() {
            if (window.innerWidth < 768) {
                itemsPerView = 1;
            } else if (window.innerWidth < 1200) {
                itemsPerView = 2;
            } else {
                itemsPerView = 3;
            }

            // Учитываем только видимые элементы
            const visibleItems = Array.from(items).filter(item =>
                item.style.display !== 'none'
            );

            totalSlides = Math.ceil(visibleItems.length / itemsPerView);

            // Сбрасываем позицию карусели
            currentIndex = 0;
            updateCarousel();
            createDots();
            updateButtons();
        }

        // Создаем точки навигации
        function createDots() {
            if (!dotsContainer) return;

            dotsContainer.innerHTML = '';

            for (let i = 0; i < totalSlides; i++) {
                const dot = document.createElement('button');
                dot.className = 'rt-carousel-dot';
                dot.setAttribute('aria-label', `Перейти к слайду ${i + 1}`);
                if (i === 0) dot.classList.add('active');
                dot.addEventListener('click', () => goToSlide(i));
                dotsContainer.appendChild(dot);
            }
        }

        // Обновляем активную точку
        function updateDots() {
            const dots = dotsContainer.querySelectorAll('.rt-carousel-dot');
            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === currentIndex);
            });
        }

        // Обновляем состояние кнопок
        function updateButtons() {
            if (!prevBtn || !nextBtn) return;

            prevBtn.disabled = currentIndex === 0;
            nextBtn.disabled = currentIndex === totalSlides - 1;

            if (prevBtn.disabled) {
                prevBtn.setAttribute('disabled', 'true');
                prevBtn.setAttribute('aria-disabled', 'true');
            } else {
                prevBtn.removeAttribute('disabled');
                prevBtn.setAttribute('aria-disabled', 'false');
            }

            if (nextBtn.disabled) {
                nextBtn.setAttribute('disabled', 'true');
                nextBtn.setAttribute('aria-disabled', 'true');
            } else {
                nextBtn.removeAttribute('disabled');
                nextBtn.setAttribute('aria-disabled', 'false');
            }
        }

        // Перемещаем карусель
        function updateCarousel() {
            if (isAnimating) return;

            isAnimating = true;

            // Рассчитываем правильное смещение
            const itemWidth = items[0].offsetWidth + 20; // width + margin
            const wrapperWidth = wrapper.offsetWidth;
            const contentWidth = items.length * itemWidth;
            const maxOffset = Math.max(0, contentWidth - wrapperWidth);
            const translateX = Math.min(maxOffset, -currentIndex * itemsPerView * itemWidth);

            carousel.style.transition = 'transform 0.4s ease';
            carousel.style.transform = `translateX(${translateX}px)`;

            updateDots();
            updateButtons();

            // Сбрасываем флаг анимации после завершения
            setTimeout(() => {
                isAnimating = false;
            }, 400);
        }

        // Переход к слайду
        function goToSlide(index) {
            if (isAnimating) return;

            currentIndex = Math.max(0, Math.min(index, totalSlides - 1));
            updateCarousel();
        }

        // Следующий слайд
        function nextSlide() {
            if (currentIndex < totalSlides - 1 && !isAnimating) {
                currentIndex++;
                updateCarousel();
            }
        }

        // Предыдущий слайд
        function prevSlide() {
            if (currentIndex > 0 && !isAnimating) {
                currentIndex--;
                updateCarousel();
            }
        }

        // Инициализация
        updateItemsPerView();

        // Обработчики событий
        if (prevBtn) {
            prevBtn.addEventListener('click', prevSlide);
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', nextSlide);
        }

        // Ресайз с debounce
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                updateItemsPerView();
            }, 250);
        });

        // Swipe для мобильных
        let touchStartX = 0;
        let touchEndX = 0;

        wrapper.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
        }, { passive: true });

        wrapper.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].clientX;
            handleSwipe();
        }, { passive: true });

        function handleSwipe() {
            if (isAnimating) return;

            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;

            if (Math.abs(diff) > swipeThreshold) {
                if (diff > 0) {
                    nextSlide();
                } else {
                    prevSlide();
                }
            }
        }
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