var fileInput = document.querySelector('input[type="file"]');
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                alert('Recipe seleccionado: ' + this.files[0].name + ' 👀');
            }
        });
    
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            if (!fileInput.value) {
                alert('Por favor selecciona un Recipe en el boton "choose file" 📂');
            } else {
                var formData = new FormData();
                formData.append('file', fileInput.files[0]);
    
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.text())
                .then(data => {
                    alert('Recipe cargado exitosamente ✅');
                    fileInput.value = ''; // Limpia el campo de archivo
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Hubo un error al cargar el Recipe ❌');
                });
            }
        });