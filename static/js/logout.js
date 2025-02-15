async function handleLogout(event) {
    event.preventDefault();
    try {
        const response = await fetch('/shopapp/logout/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'  // Важно для работы с куками
        });

        if (response.ok) {
            // После успешного выхода перенаправляем на страницу авторизации
            window.location.href = '/shopapp/auth/';
        } else {
            console.error('Ошибка при выходе');
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
}