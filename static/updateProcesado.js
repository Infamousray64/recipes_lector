document.querySelectorAll('.procesado-checkbox').forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        fetch('/update_procesado', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: this.dataset.id,
                procesado: this.checked ? 1 : 0,
            }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});   