document.addEventListener('DOMContentLoaded', function() {
    const mainImage = document.querySelector('.main-screenshot img');
    const thumbnails = document.querySelectorAll('.thumbnail');
    
    // Устанавливаем первую миниатюру как активную
    if (thumbnails.length > 0) {
        thumbnails[0].classList.add('active');
    }
    
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            const newSrc = this.getAttribute('data-src');
            
            if (newSrc) {
                // Плавное затухание
                mainImage.style.opacity = '0';
                
                // Меняем изображение после начала анимации
                setTimeout(() => {
                    mainImage.src = newSrc;
                    // Плавное появление нового изображения
                    mainImage.style.opacity = '1';
                }, 300);
                
                // Обновляем активный класс
                thumbnails.forEach(thumb => thumb.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });
    
    // Обработка загрузки основного изображения
    mainImage.addEventListener('load', function() {
        this.style.opacity = '1';
    });
    
    // Добавляем отладочную информацию
    console.log('Game detail script loaded');
    console.log('Found thumbnails:', thumbnails.length);
    console.log('Main image:', mainImage);

    const addToCartButton = document.querySelector('.add-to-cart-button');
    if (addToCartButton) {
        addToCartButton.addEventListener('click', handleAddToCart);
    }

    const reviewForm = document.getElementById('review-form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', handleReviewSubmit);
    }

    // Инициализация звездного рейтинга
    const ratingStars = document.querySelectorAll('.star-rating .star');
    const ratingInput = document.getElementById('rating-value');
    
    ratingStars.forEach(star => {
        star.addEventListener('mouseover', function() {
            const rating = this.dataset.rating;
            highlightStars(rating);
        });
        
        star.addEventListener('mouseout', function() {
            highlightStars(ratingInput.value);
        });
        
        star.addEventListener('click', function() {
            const rating = this.dataset.rating;
            ratingInput.value = rating;
            highlightStars(rating);
        });
    });

    // Загружаем отзывы при загрузке страницы
    const productId = document.getElementById('review-form')?.dataset.productId;
    if (productId) {
        loadReviews(productId);
    }
});

async function handleAddToCart(event) {
    event.preventDefault();
    
    const button = event.currentTarget;
    const gameId = button.dataset.gameId;
    
    if (!gameId) {
        showNotification('Ошибка: ID игры не найден', 'error');
        return;
    }

    try {
        // Получаем CSRF токен из cookie
        const csrftoken = getCookie('csrftoken');
        
        const response = await fetch('/app/api/cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,  // Добавляем CSRF токен
            },
            credentials: 'include',
            body: JSON.stringify({
                product_id: gameId,
                quantity: 1
            })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Игра добавлена в корзину', 'success');
            updateCartCounter();
            
            const viewCartButton = document.querySelector('.view-cart-button');
            if (viewCartButton) {
                viewCartButton.style.display = 'block';
            }
        } else {
            showNotification(data.error || 'Ошибка при добавлении в корзину', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Ошибка при добавлении в корзину', 'error');
    }
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

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Функция для отображения отзывов
function displayReviews(reviews) {
    const reviewsContainer = document.getElementById('reviews-container');
    reviewsContainer.innerHTML = reviews.map(review => `
        <div class="review-card" data-review-id="${review.id}">
            <div class="review-header">
                <span class="review-author">${review.user}</span>
                <span class="review-rating">★ ${review.rating}</span>
                ${review.is_owner ? `
                    <button class="delete-review-btn" onclick="deleteReview(${review.id})">
                        Удалить
                    </button>
                ` : ''}
            </div>
            <p class="review-comment">${review.comment}</p>
            <span class="review-date">${new Date(review.created_at).toLocaleDateString()}</span>
        </div>
    `).join('');
}

// Функция для удаления отзыва
async function deleteReview(reviewId) {
    if (!confirm('Вы уверены, что хотите удалить этот отзыв?')) {
        return;
    }

    try {
        const response = await fetch(`/app/api/review/${reviewId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Ошибка при удалении отзыва');
        }

        // Удаляем карточку отзыва из DOM
        const reviewCard = document.querySelector(`.review-card[data-review-id="${reviewId}"]`);
        if (reviewCard) {
            reviewCard.remove();
        }

        showNotification('Отзыв успешно удален', 'success');

    } catch (error) {
        console.error('Ошибка при удалении отзыва:', error);
        showNotification(error.message, 'error');
    }
}

// Функция для отправки отзыва
async function handleReviewSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const rating = form.querySelector('#rating-value').value;
    const comment = form.querySelector('#comment').value;
    const productId = form.dataset.productId;

    if (!rating || rating === '0' || !comment) {
        showNotification('Пожалуйста, поставьте оценку и напишите комментарий', 'error');
        return;
    }

    try {
        const response = await fetch('/app/api/review/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                product_id: productId,
                rating: parseInt(rating),
                comment: comment
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Ошибка при отправке отзыва');
        }

        // Очищаем форму
        form.reset();
        highlightStars(0);  // Сбрасываем звезды

        // Обновляем список отзывов
        await loadReviews(productId);
        
        showNotification('Отзыв успешно добавлен', 'success');

    } catch (error) {
        console.error('Ошибка при отправке отзыва:', error);
        showNotification(error.message, 'error');
    }
}

// Функция для загрузки отзывов
async function loadReviews(productId) {
    try {
        const response = await fetch(`/app/api/review/?product_id=${productId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Ошибка при загрузке отзывов');
        }

        displayReviews(data.reviews);

    } catch (error) {
        console.error('Ошибка при загрузке отзывов:', error);
        showNotification(error.message, 'error');
    }
}

function highlightStars(rating) {
    document.querySelectorAll('.star-rating .star').forEach(star => {
        const starRating = parseInt(star.dataset.rating);
        star.classList.toggle('active', starRating <= rating);
        star.classList.toggle('hover', starRating <= rating);
    });
} 