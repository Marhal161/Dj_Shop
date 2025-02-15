document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.screenshots-container');
    const screenshots = document.querySelectorAll('.game-screenshot');
    const prevButton = document.querySelector('.slider-button.prev');
    const nextButton = document.querySelector('.slider-button.next');
    const indicators = document.querySelectorAll('.indicator');
    
    let currentIndex = 0;
    const totalSlides = screenshots.length;

    // Функция обновления слайдера
    function updateSlider() {
        container.style.transform = `translateX(-${currentIndex * 100}%)`;
        
        // Обновляем индикаторы
        indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === currentIndex);
        });
        
        // Обновляем состояние кнопок
        prevButton.style.display = currentIndex === 0 ? 'none' : 'flex';
        nextButton.style.display = currentIndex === totalSlides - 1 ? 'none' : 'flex';
    }

    // Обработчики для кнопок
    prevButton.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateSlider();
        }
    });

    nextButton.addEventListener('click', () => {
        if (currentIndex < totalSlides - 1) {
            currentIndex++;
            updateSlider();
        }
    });

    // Обработчики для индикаторов
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            currentIndex = index;
            updateSlider();
        });
    });

    // Поддержка свайпов для мобильных устройств
    let touchStartX = 0;
    let touchEndX = 0;

    container.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    });

    container.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0 && currentIndex < totalSlides - 1) {
                // Свайп влево
                currentIndex++;
                updateSlider();
            } else if (diff < 0 && currentIndex > 0) {
                // Свайп вправо
                currentIndex--;
                updateSlider();
            }
        }
    }

    // Инициализация слайдера
    updateSlider();
}); 