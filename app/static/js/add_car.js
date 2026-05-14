let carId = null;
let isUploading = false;

const brandSelect = document.getElementById('brand-select');
const modelSelect = document.getElementById('model-select');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

// 1. Динамични модели
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

// 2. Валидация на формата
function validateForm() {
    const requiredFields = [
        'brand-select', 'model-select', 'year', 'price', 
        'horsepower', 'engine_size', 'fuel_type', 
        'mileage', 'transmission', 'doors', 'condition'
    ];

    for (let id of requiredFields) {
        let el = document.getElementById(id);
        if (!el) el = document.querySelector(`[name="${id}"]`);
        
        if (!el || !el.value) {
            let label = el?.parentElement?.querySelector('label')?.innerText.replace('*', '').trim() || id;
            return `Моля, попълнете задължителното поле: "${label}", преди да качите снимки!`;
        }
    }
    return null;
}

// 3. Основна функция за качване
async function uploadFiles(files) {
    if (isUploading || files.length === 0) return;
    
    console.log("Започва обработка на файлове...");

    if (!carId) {
        const error = validateForm();
        if (error) {
            alert(error);
            fileInput.value = ''; 
            return;
        }

        isUploading = true;
        const carForm = document.getElementById('carForm');
        const formData = new FormData(carForm);
        
        // Автоматично взимаме правилния URL адрес
        const uploadUrl = carForm.getAttribute('action') || window.location.pathname;
        
        try {
            console.log("Изпращане на заявка за създаване на обява...");
            const response = await fetch(uploadUrl, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData
            });
            
            const data = await response.json();

            if (response.ok) {
                console.log("Обявата създадена успешно! ID:", data.car_id);
                carId = data.car_id;
                
                // Блокираме полетата (визуално), за да не се променят
                const inputs = document.querySelectorAll('#carForm .custom-input');
                inputs.forEach(input => {
                    input.style.pointerEvents = 'none';
                    input.style.opacity = '0.7';
                });
                
            } else {
                console.error("Грешка от сървъра:", data);
                let msg = "Сървърът върна грешка:\n";
                if (data.errors) {
                    for (let field in data.errors) {
                        msg += `• ${data.errors[field].join(', ')}\n`;
                    }
                }
                alert(msg);
                isUploading = false;
                fileInput.value = '';
                return;
            }
        } catch (err) {
            console.error("Мрежова грешка:", err);
            alert("Възникна грешка при свързване със сървъра.");
            isUploading = false;
            fileInput.value = '';
            return;
        }
    }

    // 4. Качване на самите снимки една по една
    isUploading = true;
    for (const file of files) {
        const imageData = new FormData();
        imageData.append('file', file);

        try {
            const imgResponse = await fetch(`/upload_image/${carId}`, {
                method: 'POST',
                body: imageData
            });

            if (imgResponse.ok) {
                const result = await imgResponse.json();
                const preview = document.getElementById('preview');
                const div = document.createElement('div');
                div.className = 'col-md-3 col-6 fade-in';
                div.innerHTML = `
                    <div class="preview-card shadow-sm">
                        <img src="${result.url}" class="preview-img">
                        <div class="bg-neon text-dark text-center py-1 small fw-bold">
                            <i class="bi bi-check-circle-fill me-1"></i>Качена
                        </div>
                    </div>`;
                preview.appendChild(div);
            } else {
                console.error("Грешка при качване на снимка");
            }
        } catch (err) {
            console.error(err);
        }
    }
    isUploading = false;
    fileInput.value = ''; 
}

// 5. Event Listeners
dropZone.addEventListener('click', () => { fileInput.click(); });

fileInput.addEventListener('change', (e) => {
    uploadFiles(e.target.files);
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    uploadFiles(e.dataTransfer.files);
});

document.getElementById('carForm').addEventListener('submit', function(e) {
    if (!carId) {
        e.preventDefault();
        alert("Моля, качете поне една снимка преди да публикувате!");
    } else {
        e.preventDefault();
        window.location.href = `/car/${carId}`;
    }
});