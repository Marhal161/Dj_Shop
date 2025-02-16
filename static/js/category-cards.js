document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.category-card');

    cards.forEach(card => {
        const images = card.querySelectorAll('.stacked-image');
        let isAnimating = false;

        // Начальные позиции
        function resetPositions() {
            images.forEach((img, index) => {
                img.style.transform = `
                    translateZ(${-index * 10}px) 
                    translateY(${-index * 10}px) 
                    rotate(${-index * 4}deg)
                `;
                img.style.zIndex = images.length - index;
            });
        }

        // Анимация при наведении
        function animateIn() {
            if (isAnimating) return;
            isAnimating = true;

            images.forEach((img, index) => {
                const delay = index * 50;
                setTimeout(() => {
                    img.style.transform = `
                        translateZ(${(images.length - index) * 20}px) 
                        translateY(${-index * 15}px) 
                        rotate(${-index * 6}deg)
                    `;
                }, delay);
            });

            // Анимация самой карточки
            card.style.transform = 'translateY(-10px)';
            card.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
        }

        // Анимация при уходе курсора
        function animateOut() {
            images.forEach((img, index) => {
                const delay = index * 50;
                setTimeout(() => {
                    img.style.transform = `
                        translateZ(${-index * 10}px) 
                        translateY(${-index * 10}px) 
                        rotate(${-index * 4}deg)
                    `;
                }, delay);
            });

            // Возвращаем карточку в исходное положение
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';

            setTimeout(() => {
                isAnimating = false;
            }, images.length * 50);
        }

        // Добавляем обработчики событий
        card.addEventListener('mouseenter', animateIn);
        card.addEventListener('mouseleave', animateOut);

        // Устанавливаем начальные позиции
        resetPositions();
    });

    // Добавляем навигацию
    const grid = document.querySelector('.categories-grid');
    const prevBtn = document.querySelector('.categories-nav.prev');
    const nextBtn = document.querySelector('.categories-nav.next');

    if (prevBtn && nextBtn) {
        // Функция прокрутки
        function scroll(direction) {
            const cardWidth = 330; // Ширина карточки + gap
            const scrollAmount = direction === 'left' ? -cardWidth : cardWidth;
            
            grid.scrollBy({
                left: scrollAmount,
                behavior: 'smooth'
            });
        }

        // Обработчики для кнопок
        prevBtn.addEventListener('click', () => scroll('left'));
        nextBtn.addEventListener('click', () => scroll('right'));

        // Показываем/скрываем кнопки в зависимости от положения прокрутки
        function updateNavButtons() {
            const isStart = grid.scrollLeft === 0;
            const isEnd = grid.scrollLeft + grid.clientWidth >= grid.scrollWidth;

            prevBtn.style.opacity = isStart ? '0.5' : '1';
            prevBtn.style.pointerEvents = isStart ? 'none' : 'auto';
            
            nextBtn.style.opacity = isEnd ? '0.5' : '1';
            nextBtn.style.pointerEvents = isEnd ? 'none' : 'auto';
        }

        grid.addEventListener('scroll', updateNavButtons);
        window.addEventListener('resize', updateNavButtons);
        updateNavButtons(); // Инициализация
    }
}); 