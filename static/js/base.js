document.addEventListener('DOMContentLoaded', function() {
    // Мобильное меню с новым дизайном
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mainNav = document.querySelector('.main-nav');
    const header = document.querySelector('.header');
    
    // Создание кнопки мобильного меню если она не существует
    if (!mobileMenuBtn && window.innerWidth <= 768) {
        const menuBtn = document.createElement('button');
        menuBtn.classList.add('mobile-menu-btn');
        menuBtn.innerHTML = `
            <span></span>
            <span></span>
            <span></span>
        `;
        
        const userControls = document.querySelector('.user-controls');
        if (userControls) {
            userControls.insertBefore(menuBtn, userControls.firstChild);
        }
    }
    
    // Обработчик для мобильного меню
    document.addEventListener('click', function(e) {
        if (e.target.closest('.mobile-menu-btn')) {
            const btn = e.target.closest('.mobile-menu-btn');
            const nav = document.querySelector('.main-nav');
            
            btn.classList.toggle('active');
            nav.classList.toggle('active');
            
            // Блокируем скролл когда меню открыто
            if (nav.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        }
    });
    
    // Закрытие мобильного меню при клике на ссылку
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            const mobileBtn = document.querySelector('.mobile-menu-btn');
            const nav = document.querySelector('.main-nav');
            
            if (mobileBtn && nav) {
                mobileBtn.classList.remove('active');
                nav.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });
    
    // Закрытие мобильного меню при клике вне его
    document.addEventListener('click', function(e) {
        const nav = document.querySelector('.main-nav');
        const btn = document.querySelector('.mobile-menu-btn');
        
        if (nav && btn && nav.classList.contains('active')) {
            if (!nav.contains(e.target) && !btn.contains(e.target)) {
                btn.classList.remove('active');
                nav.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
    });

    // Обработка изменения размера окна
    window.addEventListener('resize', function() {
        const nav = document.querySelector('.main-nav');
        const btn = document.querySelector('.mobile-menu-btn');
        
        if (window.innerWidth > 768) {
            if (nav) nav.classList.remove('active');
            if (btn) btn.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
    
    // Скрытие/показ хедера при скролле
    let lastScrollY = window.scrollY;
    let ticking = false;
    
    function updateHeader() {
        const header = document.querySelector('.header');
        if (!header) return;
        
        if (window.scrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        // Скрытие хедера при скролле вниз
        if (window.scrollY > lastScrollY && window.scrollY > 200) {
            header.classList.add('hidden');
        } else {
            header.classList.remove('hidden');
        }
        
        lastScrollY = window.scrollY;
        ticking = false;
    }
    
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateHeader);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestTick);
    
    // Активная ссылка в меню
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Управление анимацией карточек
    const wrapper = document.querySelector('.game-cards-wrapper');
    if (wrapper) {
        const cards = wrapper.querySelectorAll('.game-card');
        
        // Дублируем карточки для бесконечной анимации
        cards.forEach(card => {
            const clone = card.cloneNode(true);
            wrapper.appendChild(clone);
        });

        // Устанавливаем стиль анимации
        wrapper.style.cssText = `
            animation: scroll-left 120s linear infinite;
            animation-play-state: running;
        `;

        // Добавляем обработчики для остановки анимации при наведении
        wrapper.addEventListener('mouseenter', () => {
            wrapper.style.animationPlayState = 'paused';
        });

        wrapper.addEventListener('mouseleave', () => {
            wrapper.style.animationPlayState = 'running';
        });
    }

    // Обновляем счетчик корзины при загрузке любой страницы
    console.log('DOM loaded, calling updateCartCounter');
    updateCartCounter();
});

// Функция обновления счетчика корзины
async function updateCartCounter() {
    try {
        console.log('Updating cart counter...');
        const response = await fetch('/app/api/cart/', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('Cart data:', data);

        const cartBtn = document.querySelector('.cart-btn');
        console.log('Cart button found:', cartBtn);

        if (!cartBtn) {
            console.error('Cart button not found');
            return;
        }

        let counter = cartBtn.querySelector('.cart-counter');
        console.log('Existing counter:', counter);
        
        if (data.total_items && data.total_items > 0) {
            console.log('Total items:', data.total_items);
            if (!counter) {
                counter = document.createElement('div');
                counter.className = 'cart-counter';
                cartBtn.appendChild(counter);
                console.log('Created new counter');
            }
            counter.textContent = data.total_items;
            counter.style.display = 'flex';
            console.log('Updated counter:', counter);
        } else if (counter) {
            counter.remove();
            console.log('Removed counter');
        }
    } catch (error) {
        console.error('Error updating cart counter:', error);
    }
}

// Экспортируем функцию, чтобы она была доступна в других скриптах
window.updateCartCounter = updateCartCounter; 