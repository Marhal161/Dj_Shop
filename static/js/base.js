document.addEventListener('DOMContentLoaded', function() {
    // Мобильное меню
    const menuButton = document.createElement('button');
    menuButton.classList.add('menu-toggle');
    menuButton.innerHTML = '☰';
    
    const nav = document.querySelector('.main-nav');
    const header = document.querySelector('.header-container');
    
    if (window.innerWidth <= 768) {
        header.insertBefore(menuButton, nav);
        nav.style.display = 'none';
    }
    
    menuButton.addEventListener('click', function() {
        nav.style.display = nav.style.display === 'none' ? 'block' : 'none';
    });
    
    // Обработка изменения размера окна
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            nav.style.display = 'block';
            if (menuButton.parentNode) {
                menuButton.parentNode.removeChild(menuButton);
            }
        } else {
            nav.style.display = 'none';
            if (!menuButton.parentNode) {
                header.insertBefore(menuButton, nav);
            }
        }
    });
    
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
        console.log('Updating cart counter...'); // Добавим отладочный вывод
        const response = await fetch('/shopapp/api/cart/', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('Cart data:', data);

        const cartBtn = document.querySelector('.cart-btn');
        console.log('Cart button found:', cartBtn); // Проверим наличие кнопки

        if (!cartBtn) {
            console.error('Cart button not found');
            return;
        }

        let counter = cartBtn.querySelector('.cart-counter');
        console.log('Existing counter:', counter); // Проверим существующий счетчик
        
        if (data.total_items && data.total_items > 0) {
            console.log('Total items:', data.total_items); // Проверим количество
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