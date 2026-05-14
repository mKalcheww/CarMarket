// Взимаме ID-то на колата динамично от атрибута на формата
const carId = document.getElementById('carForm').dataset.carId;
let deletedImages = [];

// Динамични модели за edit страницата
const brandSelect = document.getElementById('brand-select');
const modelSelect = document.getElementById('model-select');

brandSelect.addEventListener('change', function() {
    const brand = this.value;
    modelSelect.innerHTML = '<option value="">Зареждане...</option>';
    if (brand) {
        fetch(`/api/models/${encodeURIComponent(brand)}`)
            .then(r => r.json())
            .then(data => {
                modelSelect.innerHTML = '<option value="">Изберете модел</option>';
                data.forEach(m => {
                    let opt = document.createElement('option');
                    opt.value = opt.textContent = m;
                    modelSelect.appendChild(opt);
                });
            });
    }
});

// Функция за маркиране на изтриване
function deleteImage(imgId) {
    const container = document.getElementById(`img-container-${imgId}`);
    container.classList.add('opacity-0');
    setTimeout(() => { container.style.display = 'none'; }, 300);
    
    deletedImages.push(imgId);
    document.getElementById('deleted_image_ids').value = deletedImages.join(',');
}

// Функция за маркиране на главна снимка
function setMainImage(imgId) {
    document.getElementById('main_image_id').value = imgId;

    document.querySelectorAll('.main-badge').forEach(badge => {
        badge.style.display = 'none';
    });
    
    const badge = document.getElementById(`badge-${imgId}`);
    if (badge) {
        badge.style.display = 'block';
    }
}

// Качване на нови снимки (AJAX)
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

async function uploadFiles(files) {
    let uploaded = false;
    for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        const resp = await fetch(`/upload_image/${carId}`, { method: 'POST', body: formData });
        if (resp.ok) {
            uploaded = true;
        }
    }
    
    if (uploaded) {
        location.reload(); 
    }
}

dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => uploadFiles(e.target.files));