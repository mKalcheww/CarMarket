// Автоматично събираме src адресите на всички заредени снимки от Carousel структурата
const allImages = Array.from(document.querySelectorAll('.main-display-img')).map(img => img.src);

let currentImageIndex = 0;

function openLightbox(index) {
    currentImageIndex = index;
    updateLightboxImage();
    const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('lightboxModal'));
    modal.show();
}

function changeLightbox(direction) {
    if (allImages.length === 0) return;
    currentImageIndex += direction;
    if (currentImageIndex >= allImages.length) currentImageIndex = 0;
    if (currentImageIndex < 0) currentImageIndex = allImages.length - 1;
    updateLightboxImage();
}

function updateLightboxImage() {
    const lightboxImg = document.getElementById('lightboxImage');
    if (lightboxImg && allImages[currentImageIndex]) {
        lightboxImg.src = allImages[currentImageIndex];
    }
}

function goToSlide(index) {
    const carousel = bootstrap.Carousel.getOrCreateInstance(document.getElementById('carCarousel'));
    carousel.to(index);
}

document.addEventListener('keydown', function(e) {
    const modalEl = document.getElementById('lightboxModal');
    if (modalEl && modalEl.classList.contains('show')) {
        if (e.key === "ArrowLeft") changeLightbox(-1);
        if (e.key === "ArrowRight") changeLightbox(1);
    }
});

// Бутони за контакт с динамично чете за data-* атрибути
document.getElementById('phoneButton')?.addEventListener('click', function() {
    const phone = this.dataset.phone; // Взима стойността от data-phone
    if (phone && phone !== 'None' && phone.trim() !== '') {
         this.innerHTML = '<i class="bi bi-telephone-fill me-2"></i>' + phone;
         this.classList.remove('btn-animated', 'btn-neon');
         this.classList.add('btn-outline-neon');
    } else {
         this.innerHTML = 'Няма посочен телефон';
         this.classList.remove('btn-animated');
    }
});

document.getElementById('emailButton')?.addEventListener('click', function() {
    const email = this.dataset.email; // Взима стойността от data-email
    this.innerHTML = '<i class="bi bi-envelope-fill me-2"></i>' + email;
    this.classList.remove('btn-outline-light');
    this.classList.add('btn-outline-neon');
});