document.addEventListener('DOMContentLoaded', function() {
    // Обработчики переключения форм
    document.querySelectorAll('.toggle-form').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const showForm = this.dataset.show;
            toggleForms(showForm);
        });
    });

    // Обработка форм
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        showMessage('loginMessage', 'Выполняется вход...', false);
        const formData = new FormData(this);

        try {
            const response = await fetch(this.action, {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showMessage('loginMessage', data.message || 'Вход выполнен успешно!', false);
                // Редирект после успешного входа
                setTimeout(() => {
                    window.location.href = '/shopapp/';
                }, 1500);
            } else {
                // Обработка различных типов ошибок
                let errorMessage = 'Ошибка при входе';
                if (data.errors) {
                    if (typeof data.errors === 'object') {
                        errorMessage = Object.values(data.errors).flat().join('\n');
                    } else if (Array.isArray(data.errors)) {
                        errorMessage = data.errors.join('\n');
                    } else {
                        errorMessage = data.errors;
                    }
                } else if (data.message) {
                    errorMessage = data.message;
                }
                showMessage('loginMessage', errorMessage, true);
            }
        } catch (error) {
            console.error('Ошибка:', error);
            showMessage('loginMessage', 'Произошла ошибка при отправке данных', true);
        }
    });

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        showMessage('registerMessage', 'Выполняется регистрация...', false);
        const formData = new FormData(this);

        try {
            const response = await fetch(this.action, {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showMessage('registerMessage', data.message || 'Регистрация успешна!', false);
                // Переключение на форму входа после успешной регистрации
                setTimeout(() => {
                    toggleForms('login');
                }, 1500);
            } else {
                // Обработка различных типов ошибок
                let errorMessage = 'Ошибка при регистрации';
                if (data.errors) {
                    if (typeof data.errors === 'object') {
                        errorMessage = Object.values(data.errors).flat().join('\n');
                    } else if (Array.isArray(data.errors)) {
                        errorMessage = data.errors.join('\n');
                    } else {
                        errorMessage = data.errors;
                    }
                } else if (data.message) {
                    errorMessage = data.message;
                }
                showMessage('registerMessage', errorMessage, true);
            }
        } catch (error) {
            console.error('Ошибка:', error);
            showMessage('registerMessage', 'Произошла ошибка при отправке данных', true);
        }
    });
});

function toggleForms(showForm) {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (showForm === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        // Очищаем сообщения и поля
        document.getElementById('loginMessage').textContent = '';
        loginForm.reset();
    } else {
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
        // Очищаем сообщения и поля
        document.getElementById('registerMessage').textContent = '';
        registerForm.reset();
    }
}

function showMessage(elementId, message, isError = false) {
    const messageDiv = document.getElementById(elementId);
    if (messageDiv) {
        // Обработка многострочных сообщений
        if (message.includes('\n')) {
            messageDiv.innerHTML = message.split('\n').join('<br>');
        } else {
            messageDiv.textContent = message;
        }
        messageDiv.className = 'message ' + (isError ? 'error' : 'success');
    }
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
    }
}

function handleLogout(event) {
    event.preventDefault();
    console.log('Logout function called');
    
    // Показываем подтверждение
    if (!confirm('Вы уверены, что хотите выйти?')) {
        return;
    }
    
    console.log('Sending logout request');
    
    fetch('/shopapp/api/logout/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'include'
    })
    .then(response => {
        console.log('Response received:', response.status);
        if (response.ok) {
            return response.json();
        }
        throw new Error('Logout failed');
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.success) {
            // Очищаем локальное состояние
            localStorage.clear();
            sessionStorage.clear();
            
            // Перенаправляем на страницу авторизации
            window.location.href = '/shopapp/auth/';
        } else {
            console.error('Logout failed:', data.message);
            window.location.href = '/shopapp/auth/';
        }
    })
    .catch(error => {
        console.error('Error during logout:', error);
        window.location.href = '/shopapp/auth/';
    });
}

// Функция для получения значения cookie
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

// Убедимся, что скрипт загружен
console.log('Auth.js loaded');