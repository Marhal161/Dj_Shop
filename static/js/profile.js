// Функция загрузки данных профиля
async function fetchProfileData() {
    try {
        console.log('Начало загрузки данных профиля');
        const [profileResponse, transactionsResponse] = await Promise.all([
            fetch('/app/api/profile/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            }),
            fetch('/app/api/profile/balance/transactions/', {  // Новый эндпоинт для истории транзакций
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            })
        ]);

        if (!profileResponse.ok || !transactionsResponse.ok) {
            throw new Error('Ошибка получения данных');
        }

        const [profileData, transactionsData] = await Promise.all([
            profileResponse.json(),
            transactionsResponse.json()
        ]);

        console.log('Полученные данные профиля:', profileData);
        console.log('История транзакций:', transactionsData);

        // Обновляем данные профиля
        updateProfileData(profileData);
        // Обновляем историю транзакций
        updateTransactionsList(transactionsData);
        
    } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
        showNotification('Ошибка загрузки данных', 'error');
    }
}

// Функция обновления данных профиля
function updateProfileData(data) {
    document.getElementById('firstName').value = data.first_name || '';
    document.getElementById('lastName').value = data.last_name || '';
    document.getElementById('email').value = data.email || '';
    
    // Обновляем инициалы в аватаре
    updateAvatar(data.first_name, data.last_name);
    
    const userFullName = document.getElementById('userFullName');
    if (userFullName) {
        userFullName.textContent = `${data.first_name} ${data.last_name}`.trim() || data.username;
    }
    
    const balanceElement = document.getElementById('currentBalance');
    if (balanceElement) {
        const balance = typeof data.balance === 'number' ? data.balance : parseFloat(data.balance) || 0;
        balanceElement.textContent = balance.toFixed(2);
    }
}

// Функция обновления аватара
function updateAvatar(firstName, lastName) {
    const initialsElement = document.querySelector('.initials');
    if (initialsElement) {
        let initials = '';
        if (firstName) initials += firstName.charAt(0);
        if (lastName) initials += lastName.charAt(0);
        initialsElement.textContent = initials.toUpperCase() || '?';
        
        // Генерируем цвет на основе имени
        const avatarCircle = document.querySelector('.avatar-circle');
        if (avatarCircle) {
            const colors = [
                '#2ecc71', '#3498db', '#9b59b6', '#f1c40f', 
                '#e74c3c', '#1abc9c', '#34495e', '#e67e22'
            ];
            const colorIndex = Math.abs(
                (firstName + lastName).split('').reduce(
                    (acc, char) => acc + char.charCodeAt(0), 0
                )
            ) % colors.length;
            avatarCircle.style.backgroundColor = colors[colorIndex];
        }
    }
}

// Функция обновления списка транзакций
function updateTransactionsList(transactions) {
    const transactionsList = document.getElementById('transactionsList');
    if (!transactionsList) return;

    transactionsList.innerHTML = '';

    if (transactions.length === 0) {
        transactionsList.innerHTML = '<div class="transaction-item">История операций пуста</div>';
        return;
    }

    transactions.forEach(transaction => {
        const transactionElement = document.createElement('div');
        transactionElement.className = 'transaction-item';
        
        const date = new Date(transaction.created_at).toLocaleString('ru-RU');
        const amount = parseFloat(transaction.amount).toFixed(2);
        
        let transactionClass = '';
        let sign = '';
        let description = transaction.description || '';
        let gameKeyHtml = '';

        switch(transaction.transaction_type) {
            case 'DEPOSIT':
                transactionClass = 'deposit';
                sign = '+';
                if (!description) description = 'Пополнение баланса';
                break;
            case 'WITHDRAW':
                transactionClass = 'withdraw';
                sign = '-';
                if (!description) description = 'Списание средств';
                break;
            case 'PURCHASE_FAILED':
                transactionClass = 'failed';
                sign = '';
                if (!description) description = 'Неудачная попытка покупки';
                break;
            case 'PURCHASE_SUCCESS':
                transactionClass = 'success';
                sign = '-';
                if (!description) description = 'Успешная покупка игры';
                if (transaction.game_key) {
                    gameKeyHtml = `<div class="game-key">Ключ: <span>${transaction.game_key}</span></div>`;
                }
                break;
        }
        
        transactionElement.innerHTML = `
            <div class="transaction-info">
                <div class="transaction-details">
                    <span class="transaction-type">${description}</span>
                    ${gameKeyHtml}
                    <span class="transaction-date">${date}</span>
                </div>
                <span class="transaction-amount ${transactionClass}">${sign}${amount} ₽</span>
            </div>
        `;
        
        transactionsList.appendChild(transactionElement);
    });
}

// Убедимся, что DOM полностью загружен перед выполнением скрипта
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePage);
} else {
    initializePage();
}

function initializePage() {
    console.log('Инициализация страницы');
    fetchProfileData();
    
    // Инициализация форм
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileUpdate);
    }
    
    const balanceForm = document.getElementById('balanceForm');
    if (balanceForm) {
        balanceForm.addEventListener('submit', handleBalanceUpdate);
    }
}

// Функция обновления профиля
async function handleProfileUpdate(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const data = {
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        email: formData.get('email')
    };

    try {
        const response = await fetch('/app/api/profile/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Ошибка обновления профиля');
        }

        showNotification('Профиль успешно обновлен', 'success');
        fetchProfileData(); // Перезагружаем данные
        
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка обновления профиля', 'error');
    }
}

// Функция обновления баланса
async function handleBalanceUpdate(event) {
    event.preventDefault();
    
    const amount = document.getElementById('amount').value;
    console.log('Сумма пополнения:', amount);
    
    try {
        const response = await fetch('/app/api/profile/balance/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ amount: parseFloat(amount) })
        });

        if (!response.ok) {
            throw new Error('Ошибка пополнения баланса');
        }

        const data = await response.json();
        console.log('Ответ сервера после пополнения:', data);
        
        // Обновляем отображение баланса
        const balanceElement = document.getElementById('currentBalance');
        if (balanceElement) {
            balanceElement.textContent = parseFloat(data.new_balance).toFixed(2);
        }
        
        document.getElementById('amount').value = '';
        showNotification('Баланс успешно пополнен', 'success');
        
        // Обновляем все данные профиля
        await fetchProfileData();
        
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification('Ошибка пополнения баланса', 'error');
    }
}

// Функция отображения уведомлений
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Обработчик выхода
async function handleLogout(event) {
    event.preventDefault();
    
    try {
        const response = await fetch('/app/api/logout/', {
            method: 'POST',
            credentials: 'include'
        });

        if (response.ok) {
            window.location.href = '/app/auth/';
        } else {
            showNotification('Ошибка при выходе из системы', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Ошибка при выходе из системы', 'error');
    }
}