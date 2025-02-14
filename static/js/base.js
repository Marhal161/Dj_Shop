document.addEventListener('DOMContentLoaded', function() {
    // Мобильное меню
    const menuButton = document.createElement('button');
    menuButton.classList.add('menu-toggle');
    menuButton.innerHTML = '☰';
    
    const nav = document.querySelector('.main-nav');
    const header = document.querySelector('.header-container');
    
    if (window.innerWidth <= 768) {
        header.insertBefore(menuButton, nav);
        nav.style.display = 'none';
    }
    
    menuButton.addEventListener('click', function() {
        nav.style.display = nav.style.display === 'none' ? 'block' : 'none';
    });
    
    // Обработка изменения размера окна
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            nav.style.display = 'block';
            if (menuButton.parentNode) {
                menuButton.parentNode.removeChild(menuButton);
            }
        } else {
            nav.style.display = 'none';
            if (!menuButton.parentNode) {
                header.insertBefore(menuButton, nav);
            }
        }
    });
    
    // Активная ссылка в меню
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}); 