// В начале файла
console.log('Games.js loaded');

// Функция для обновления URL без перезагрузки страницы
function updateURL(filters) {
    const url = new URL(window.location.href);
    // Очищаем текущие параметры
    url.search = '';
    const params = new URLSearchParams(url.search);
    
    // Добавляем новые параметры из фильтров
    if (filters.categories && filters.categories.length > 0) {
        filters.categories.forEach(cat => {
            params.append('category', cat);
        });
    }
    
    // Обновляем URL без перезагрузки страницы
    window.history.pushState({}, '', `${url.pathname}${params.toString() ? '?' + params.toString() : ''}`);
}

// Функция для загрузки и отображения игр
async function loadGames(filters = {}) {
    try {
        let url = '/shopapp/api/games/';
        const params = new URLSearchParams();

        if (filters.categories && filters.categories.length > 0) {
            filters.categories.forEach(categoryId => {
                params.append('category', categoryId);
            });
        }
        
        const queryString = params.toString();
        if (queryString) {
            url = `${url}?${queryString}`;
        }

        // Обновляем URL в браузере
        updateURL(filters);

        const response = await fetch(url);
        const data = await response.json();

        const gamesContainer = document.getElementById('games-container');
        gamesContainer.innerHTML = '';

        if (data.games && data.games.length > 0) {
            data.games.forEach(game => {
                const gameCard = createGameCard(game);
                gamesContainer.appendChild(gameCard);
                requestAnimationFrame(() => {
                    gameCard.classList.add('visible');
                });
            });
        } else {
            gamesContainer.innerHTML = '<p class="no-games">Игры не найдены</p>';
        }
    } catch (error) {
        console.error('Error loading games:', error);
    }
}

// Функция для создания карточки игры
function createGameCard(game) {
    const card = document.createElement('div');
    card.className = 'game-card';
    
    card.innerHTML = `
        <a href="/shopapp/game/${game.id}/" class="game-link">
            <div class="game-image-container">
                <img src="${game.screenshot_url || '/static/images/no-image.png'}" 
                     alt="${game.name}" 
                     class="game-image">
            </div>
            <div class="game-info">
                <h3 class="game-title">${game.name}</h3>
                <p class="game-description">${game.description.substring(0, 150)}${game.description.length > 150 ? '...' : ''}</p>
                <div class="game-details">
                    <div class="game-categories">
                        ${game.categories.map(cat => 
                            `<span class="category-tag">${cat.name}</span>`
                        ).join('')}
                    </div>
                    <div class="game-stats">
                        <div class="game-rating">
                            ${game.rating ? `★ ${game.rating.toFixed(1)}` : 'Нет оценок'}
                        </div>
                        <p class="game-price">${game.price} ₽</p>
                        <p class="game-quantity">${game.quantity > 0 ? `В наличии: ${game.quantity} шт.` : 'Нет в наличии'}</p>
                    </div>
                    ${game.quantity > 0 ? 
                        `<button onclick="event.preventDefault(); addToCart(${game.id})" 
                                 class="buy-button">В корзину</button>` :
                        `<button class="buy-button disabled" disabled>Нет в наличии</button>`
                    }
                </div>
            </div>
        </a>
    `;
    
    return card;
}

// Функция для загрузки категорий
async function loadCategories() {
    try {
        const response = await fetch('/shopapp/api/categories/');
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Ошибка загрузки категорий');
        }
        
        const categoriesContainer = document.getElementById('categories-container');
        categoriesContainer.innerHTML = '';
        
        if (!data.categories || data.categories.length === 0) {
            categoriesContainer.innerHTML = '<p>Категории не найдены</p>';
            return;
        }
        
        data.categories.forEach(category => {
            const label = document.createElement('label');
            label.className = 'filter-checkbox';
            label.innerHTML = `
                <input type="checkbox" name="category" value="${category.id}">
                <span>${category.name}</span>
            `;
            
            // Добавляем обработчик изменения для каждого чекбокса
            const checkbox = label.querySelector('input[type="checkbox"]');
            checkbox.addEventListener('change', applyFilters);
            
            categoriesContainer.appendChild(label);
        });

        // Проверяем URL параметры для установки начальных значений
        const urlParams = new URLSearchParams(window.location.search);
        const categoryIds = urlParams.getAll('category');
        if (categoryIds.length > 0) {
            categoryIds.forEach(id => {
                const checkbox = categoriesContainer.querySelector(`input[value="${id}"]`);
                if (checkbox) {
                    checkbox.checked = true;
                }
            });
        }
    } catch (error) {
        console.error('Ошибка при загрузке категорий:', error);
        const categoriesContainer = document.getElementById('categories-container');
        categoriesContainer.innerHTML = '<p class="error">Ошибка при загрузке категорий</p>';
    }
}

// Функция сброса фильтров
function resetFilters() {
    // Очищаем поиск
    document.getElementById('search-input').value = '';
    
    // Очищаем поля цены
    document.getElementById('min-price').value = '';
    document.getElementById('max-price').value = '';
    
    // Сбрасываем сортировку
    document.getElementById('sort-select').value = 'name';
    
    // Очищаем чекбоксы категорий
    document.querySelectorAll('input[name="category"]').forEach(cb => {
        cb.checked = false;
    });
    
    // Очищаем чекбоксы рейтинга
    document.querySelectorAll('input[name="rating"]').forEach(cb => {
        cb.checked = false;
    });
    
    // Сбрасываем URL и загружаем все игры
    history.pushState({}, '', window.location.pathname);
    loadGames();
}

// Функция для сбора всех фильтров
function getFilters() {
    const filters = {};
    
    // Собираем выбранные категории только из чекбоксов
    const selectedCategories = Array.from(document.querySelectorAll('input[name="category"]:checked'))
        .map(input => input.value);
    
    if (selectedCategories.length > 0) {
        filters.categories = selectedCategories;
    }
    
    return filters;
}

// Функция применения фильтров
function applyFilters() {
    // Получаем все значения фильтров
    const searchQuery = document.getElementById('search-input').value;
    const minPrice = document.getElementById('min-price').value;
    const maxPrice = document.getElementById('max-price').value;
    const sortBy = document.getElementById('sort-select').value;
    const selectedCategories = Array.from(document.querySelectorAll('input[name="category"]:checked'))
        .map(cb => cb.value);
    const selectedRatings = Array.from(document.querySelectorAll('input[name="rating"]:checked'))
        .map(cb => cb.value);

    // Формируем параметры запроса
    const params = new URLSearchParams();

    // Добавляем параметры только если они не пустые
    if (searchQuery) {
        params.append('search', searchQuery);
    }
    if (minPrice) {
        params.append('min_price', minPrice);
    }
    if (maxPrice) {
        params.append('max_price', maxPrice);
    }
    if (sortBy) {
        params.append('sort', sortBy);
    }
    
    // Добавляем категории
    if (selectedCategories.length > 0) {
        params.append('categories', selectedCategories.join(','));
    }
    
    // Добавляем рейтинги
    if (selectedRatings.length > 0) {
        params.append('rating', selectedRatings.join(','));
    }

    // Обновляем URL и загружаем отфильтрованные игры
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    history.pushState({}, '', newUrl);
    loadGames();
}

// Добавляем обработчики событий для всех элементов фильтрации
document.addEventListener('DOMContentLoaded', function() {
    // Загружаем категории при загрузке страницы
    loadCategories();

    // Поиск с debounce
    const searchInput = document.getElementById('search-input');
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(applyFilters, 300);
    });

    // Цена
    const minPriceInput = document.getElementById('min-price');
    const maxPriceInput = document.getElementById('max-price');
    minPriceInput.addEventListener('change', applyFilters);
    maxPriceInput.addEventListener('change', applyFilters);

    // Сортировка
    const sortSelect = document.getElementById('sort-select');
    sortSelect.addEventListener('change', applyFilters);

    // Рейтинг
    document.querySelectorAll('input[name="rating"]').forEach(checkbox => {
        checkbox.addEventListener('change', applyFilters);
    });

    // Кнопка сброса
    const resetButton = document.querySelector('.reset-filters');
    if (resetButton) {
        resetButton.addEventListener('click', resetFilters);
    }

    // Загружаем игры при первой загрузке страницы
    loadGames();

    // Добавляем в начало файла или после DOMContentLoaded
    function initializeFilters() {
        const filtersToggle = document.getElementById('filters-toggle');
        const filtersSidebar = document.getElementById('filters-sidebar');
        const filtersClose = document.getElementById('filters-close');
        let overlay;

        // Создаем оверлей
        function createOverlay() {
            overlay = document.createElement('div');
            overlay.className = 'overlay';
            document.body.appendChild(overlay);
        }

        // Открываем фильтры
        function openFilters() {
            filtersSidebar.classList.add('active');
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden'; // Блокируем прокрутку основного контента
        }

        // Закрываем фильтры
        function closeFilters() {
            filtersSidebar.classList.remove('active');
            overlay.classList.remove('active');
            document.body.style.overflow = ''; // Возвращаем прокрутку
        }

        if (filtersToggle && filtersSidebar && filtersClose) {
            createOverlay();

            filtersToggle.addEventListener('click', openFilters);
            filtersClose.addEventListener('click', closeFilters);
            overlay.addEventListener('click', closeFilters);

            // Добавляем обработку свайпов
            let touchStartX = 0;
            let touchEndX = 0;

            filtersSidebar.addEventListener('touchstart', e => {
                touchStartX = e.changedTouches[0].screenX;
            }, false);

            filtersSidebar.addEventListener('touchend', e => {
                touchEndX = e.changedTouches[0].screenX;
                handleSwipe();
            }, false);

            function handleSwipe() {
                const swipeThreshold = 100; // Минимальное расстояние для свайпа
                const diff = touchStartX - touchEndX;

                if (Math.abs(diff) > swipeThreshold) {
                    if (diff > 0) {
                        // Свайп влево - закрываем фильтры
                        closeFilters();
                    }
                }
            }
        }
    }

    // Добавляем вызов функции в обработчик DOMContentLoaded
    initializeFilters();
});

// Обновляем функцию loadGames для работы с параметрами
async function loadGames() {
    const gamesContainer = document.getElementById('games-container');
    gamesContainer.innerHTML = '<div class="loading">Загрузка...</div>';

    try {
        const response = await fetch(`/shopapp/api/games/${window.location.search}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Ошибка загрузки игр');
        }

        if (!data.games || data.games.length === 0) {
            gamesContainer.innerHTML = '<div class="no-results">Игры не найдены</div>';
            return;
        }

        const gameCards = data.games.map(game => {
            const card = document.createElement('div');
            card.className = 'game-card';
            
            card.innerHTML = `
                <a href="/shopapp/game/${game.id}/" class="game-link">
                    <div class="game-image-container">
                        <img src="${game.screenshot_url || '/static/images/no-image.png'}" 
                             alt="${game.name}" 
                             class="game-image">
                    </div>
                    <div class="game-info">
                        <h3 class="game-title">${game.name}</h3>
                        <p class="game-description">${game.description.substring(0, 150)}${game.description.length > 150 ? '...' : ''}</p>
                        <div class="game-details">
                            <div class="game-categories">
                                ${game.categories.map(cat => 
                                    `<span class="category-tag">${cat.name}</span>`
                                ).join('')}
                            </div>
                            <div class="game-stats">
                                <div class="game-rating">
                                    ${game.rating ? `★ ${game.rating.toFixed(1)}` : 'Нет оценок'}
                                </div>
                                <p class="game-price">${game.price} ₽</p>
                                <p class="game-quantity">${game.quantity > 0 ? `В наличии: ${game.quantity} шт.` : 'Нет в наличии'}</p>
                            </div>
                            ${game.quantity > 0 ? 
                                `<button onclick="event.preventDefault(); addToCart(${game.id})" 
                                         class="buy-button">В корзину</button>` :
                                `<button class="buy-button disabled" disabled>Нет в наличии</button>`
                            }
                        </div>
                    </div>
                </a>
            `;
            
            return card;
        });

        gamesContainer.innerHTML = '';
        gameCards.forEach(card => {
            gamesContainer.appendChild(card);
            setTimeout(() => {
                card.classList.add('visible');
            }, 10);
        });

    } catch (error) {
        console.error('Ошибка при загрузке игр:', error);
        gamesContainer.innerHTML = `<div class="error">Ошибка при загрузке игр: ${error.message}</div>`;
    }
}

// Добавляем функцию для добавления в корзину
async function addToCart(gameId) {
    try {
        const response = await fetch('/shopapp/api/cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')  // Получаем CSRF токен
            },
            body: JSON.stringify({
                product_id: gameId,
                quantity: 1
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Ошибка при добавлении в корзину');
        }

        // Показываем уведомление об успешном добавлении
        showNotification('Игра добавлена в корзину', 'success');

    } catch (error) {
        console.error('Ошибка при добавлении в корзину:', error);
        showNotification(error.message, 'error');
    }
}

// Функция для получения CSRF токена из cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Функция для показа уведомлений
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Удаляем уведомление через 3 секунды
    setTimeout(() => {
        notification.remove();
    }, 3000);
} 