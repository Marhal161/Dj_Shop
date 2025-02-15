// Функция загрузки данных профиля
async function fetchProfileData() {
    try {
        console.log('Начало загрузки данных профиля');
        const [profileResponse, transactionsResponse] = await Promise.all([
            fetch('/shopapp/api/profile/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            }),
            fetch('/shopapp/api/profile/balance/transactions/', {  // Новый эндпоинт для истории транзакций
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

// Функция обновления списка транзакций
function updateTransactionsList(transactions) {
    const transactionsList = document.getElementById('transactionsList');
    if (!transactionsList) return;

    transactionsList.innerHTML = ''; // Очищаем список

    if (transactions.length === 0) {
        transactionsList.innerHTML = '<div class="transaction-item">История операций пуста</div>';
        return;
    }

    transactions.forEach(transaction => {
        const transactionElement = document.createElement('div');
        transactionElement.className = 'transaction-item';
        
        const date = new Date(transaction.created_at).toLocaleString('ru-RU');
        const amount = parseFloat(transaction.amount).toFixed(2);
        
        transactionElement.innerHTML = `
            <div class="transaction-info">
                <span class="transaction-type">Пополнение</span>
                <span class="transaction-date">${date}</span>
            </div>
            <span class="transaction-amount deposit">+${amount} ₽</span>
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
        const response = await fetch('/shopapp/api/profile/', {
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
        const response = await fetch('/shopapp/api/profile/balance/', {
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
function handleLogout(event) {
    event.preventDefault();
    
    fetch('/shopapp/api/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/auth/';
        } else {
            throw new Error('Ошибка при выходе');
        }
    })
    .catch(error => {
        showNotification('Ошибка при выходе из системы', 'error');
    });
} 