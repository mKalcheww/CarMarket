    // JS за динамични модели
    document.getElementById('brand-search').addEventListener('change', function() {
        const brand = this.value;
        const modelSelect = document.getElementById('model-search');
        modelSelect.innerHTML = '<option value="">Зареждане...</option>';
        if (brand) {
            fetch(`/api/models/${encodeURIComponent(brand)}`)
                .then(response => response.json())
                .then(models => {
                    modelSelect.innerHTML = '<option value="">Всички модели</option>';
                    models.forEach(m => {
                        let opt = document.createElement('option');
                        opt.value = m;
                        opt.textContent = m;
                        modelSelect.appendChild(opt);
                    });
                });
        } else {
            modelSelect.innerHTML = '<option value="">Всички модели</option>';
        }
    });