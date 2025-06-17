 document.addEventListener('DOMContentLoaded', function() {
    loadCart();

    // Добавляем обработчик для кнопки оформления заказа
    const checkoutButton = document.getElementById('checkout-button');
    if (checkoutButton) {
        checkoutButton.addEventListener('click', handleCheckout);
    }
});

async function loadCart() {
    try {
        const response = await fetch('/app/api/cart/', {
            credentials: 'include'
        });
        const data = await response.json();

        updateCartDisplay(data);
    } catch (error) {
        console.error('Error loading cart:', error);
        showNotification('Ошибка при загрузке корзины', 'error');
    }
}

function updateCartDisplay(data) {
    const cartItems = document.getElementById('cart-items');
    const totalPrice = document.getElementById('cart-total-price');

    if (!data.items || data.items.length === 0) {
        cartItems.innerHTML = '<div class="empty-cart">Корзина пуста</div>';
        totalPrice.textContent = '0';
        return;
    }

    cartItems.innerHTML = data.items.map(item => `
        <div class="cart-item" data-id="${item.id}">
            <div class="cart-item-info">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">${item.price} ₽</div>
            </div>
            <div class="cart-item-quantity">
                <button class="quantity-button" onclick="updateQuantity(${item.id}, -1)">-</button>
                <span>${item.quantity}</span>
                <button class="quantity-button" onclick="updateQuantity(${item.id}, 1)">+</button>
            </div>
            <button class="remove-button" onclick="removeItem(${item.id})">Удалить</button>
        </div>
    `).join('');

    totalPrice.textContent = data.total;
}

async function updateQuantity(itemId, change) {
    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await fetch(`/app/api/cart/items/${itemId}/update/`, {
            method: 'PATCH',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ change: change })
        });

        const data = await response.json();
        
        if (response.ok) {
            if (data.error) {
                showNotification(data.error, 'error');
            } else {
                loadCart();
                if (change > 0) {
                    showNotification('Количество товара увеличено', 'success');
                } else {
                    showNotification('Количество товара уменьшено', 'success');
                }
            }
        } else {
            showNotification(data.error || 'Ошибка при обновлении количества', 'error');
        }
    } catch (error) {
        console.error('Error updating quantity:', error);
        showNotification('Ошибка при обновлении количества', 'error');
    }
}

async function removeItem(itemId) {
    try {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await fetch(`/app/api/cart/items/${itemId}/`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        if (response.ok) {
            loadCart();
            showNotification('Товар удален из корзины', 'success');
        } else {
            const errorData = await response.json();
            showNotification(errorData.error || 'Ошибка при удалении товара', 'error');
        }
    } catch (error) {
        console.error('Error removing item:', error);
        showNotification('Ошибка при удалении товара', 'error');
    }
}

async function handleCheckout() {
    try {
        const response = await fetch('/app/api/cart/checkout/', {
            method: 'POST',
            credentials: 'include'
        });

        const data = await response.json();

        if (response.ok) {
            showPurchaseSuccess(data);
            loadCart();
        } else {
            if (data.redirect) {
                showNotification(data.error, 'error');
                setTimeout(() => {
                    window.location.href = data.redirect_url;
                }, 2000);
            } else {
                showNotification(data.error, 'error');
            }
        }
    } catch (error) {
        console.error('Error during checkout:', error);
        showNotification('Ошибка при оформлении заказа', 'error');
    }
}

function showPurchaseSuccess(data) {
    const modal = document.createElement('div');
    modal.className = 'purchase-modal';
    modal.innerHTML = `
        <div class="purchase-modal-content">
            <h2>Покупка успешно оформлена!</h2>
            <div class="purchases-list">
                ${data.purchases.map(p => `
                    <div class="purchase-item">
                        <div class="game-name">${p.game_name}</div>
                        <div class="game-key">Ключ: <span>${p.game_key}</span></div>
                        <div class="price">${p.price} ₽</div>
                    </div>
                `).join('')}
            </div>
            <div class="purchase-summary">
                <div>Итого: ${data.total_price} ₽</div>
                <div>Новый баланс: ${data.new_balance} ₽</div>
            </div>
            <button onclick="this.closest('.purchase-modal').remove()">Закрыть</button>
        </div>
    `;
    document.body.appendChild(modal);
}

function showNotification(message, type) {
    // Удаляем предыдущие уведомления
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Добавляем анимацию исчезновения перед удалением
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.5s ease-out';
        setTimeout(() => {
            notification.remove();
        }, 450);
    }, 2500);
} 