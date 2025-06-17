document.addEventListener('DOMContentLoaded', function() {
    // Получаем ID продукта из URL
    const productId = window.location.pathname.split('/').filter(Boolean).pop();
    
    // Настройка звездного рейтинга
    const starContainer = document.querySelector('.star-rating');
    const stars = document.querySelectorAll('.star');
    const ratingInput = document.getElementById('rating-value');
    
    if (starContainer) {
        // Устанавливаем начальный рейтинг в 0 (ни одной звезды)
        ratingInput.value = '0';
        
        // Обработка наведения на звезды
        stars.forEach(star => {
            star.addEventListener('mouseover', function() {
                const rating = this.dataset.rating;
                hoverStars(rating);
            });
            
            star.addEventListener('mouseout', function() {
                hoverStars(0);
                // Восстанавливаем активные звезды
                updateStars(ratingInput.value);
            });
            
            star.addEventListener('click', function() {
                const rating = this.dataset.rating;
                ratingInput.value = rating;
                updateStars(rating);
            });
        });
    }
    
    function updateStars(rating) {
        stars.forEach(star => {
            const starRating = star.dataset.rating;
            star.classList.toggle('active', starRating <= rating);
        });
    }
    
    function hoverStars(rating) {
        stars.forEach(star => {
            const starRating = star.dataset.rating;
            star.classList.toggle('hover', starRating <= rating);
        });
    }
    
    // Функция загрузки отзывов
    function loadReviews() {
            fetch(`/app/api/review/?product_id=${productId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const container = document.getElementById('reviews-container');
                    container.innerHTML = ''; // Очищаем контейнер
                    
                    data.reviews.forEach(review => {
                        // Создаем строку со звездами
                        const stars = Array(5).fill(0).map((_, index) => 
                            `<span class="star${index < review.rating ? '' : '-empty'}">★</span>`
                        ).join('');

                        container.innerHTML += `
                            <div class="review-item">
                                <div class="review-header">
                                    <span class="review-author">${review.user_name}</span>
                                    <span class="review-date">${review.created_at}</span>
                                </div>
                                <div class="review-rating">
                                    ${stars}
                                </div>
                                <div class="review-comment">
                                    ${review.comment}
                                </div>
                            </div>
                        `;
                    });
                }
            })
            .catch(error => console.error('Error loading reviews:', error));
    }
    
    // Загружаем отзывы при загрузке страницы
    loadReviews();
    
    // Обработка отправки формы отзыва
    const reviewForm = document.getElementById('review-form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const rating = this.querySelector('#rating-value').value;
            const ratingError = this.querySelector('.rating-error');
            
            // Проверяем, выбрана ли оценка
            if (rating === '0') {
                ratingError.style.display = 'block';
                return;
            }
            ratingError.style.display = 'none';
            
            const formData = {
                product: productId,
                rating: rating,
                comment: this.comment.value
            };
            
            fetch('/app/api/review/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Очищаем форму
                    this.comment.value = '';
                    // Сбрасываем рейтинг на 0 звезд
                    ratingInput.value = '0';
                    updateStars(0);
                    // Перезагружаем отзывы
                    loadReviews();
                }
            })
            .catch(error => console.error('Error posting review:', error));
        });
    }
}); 