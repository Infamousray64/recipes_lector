document.querySelectorAll('.status-checkbox').forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        var status = this.dataset.status;
        var isChecked = this.checked;

        // Deshabilitar o habilitar las casillas de total basado en el estado de las casillas parciales
        if (status === 'cotizado_parcial' || status === 'facturado_parcial') {
            let totalStatus = status.replace('parcial', 'total');
            let totalCheckbox = this.closest('td').querySelector(`input[data-status="${totalStatus}"]`);
            if (isChecked) {
                if (totalCheckbox) {
                    totalCheckbox.checked = false;
                    totalCheckbox.disabled = true;
                }
            } else {
                // Revisar si se puede habilitar la casilla de total al desmarcar parcial
                let canEnableTotal = true;
                if (status === 'facturado_parcial') {
                    let cotizadoTotalCheckbox = this.closest('td').querySelector('input[data-status="cotizado_total"]');
                    canEnableTotal = cotizadoTotalCheckbox && cotizadoTotalCheckbox.checked;
                }
                if (canEnableTotal && totalCheckbox) {
                    totalCheckbox.disabled = false;
                }
            }
        }

        if (isChecked) {
            var prevCheckboxes;

            if (status === 'cotizado_parcial') {
                prevCheckboxes = this.closest('td').querySelectorAll('input[data-status="en_proceso"]');
            } else if (status === 'cotizado_total') {
                prevCheckboxes = this.closest('td').querySelectorAll('input[data-status="en_proceso"], input[data-status="cotizado_parcial"]');
            } else if (status === 'facturado_parcial') {
                prevCheckboxes = this.closest('td').querySelectorAll('input[data-status="cotizado_parcial"]');
            } else if (status === 'facturado_total') {
                prevCheckboxes = this.closest('td').querySelectorAll('input[data-status="cotizado_total"]');
            }

            if (prevCheckboxes && Array.from(prevCheckboxes).some(checkbox => !checkbox.checked)) {
                alert('Asegurate de avanzar los status anteriores seleccionando su respectivo check-box.');
                this.checked = false;
                // Si se desmarca debido a una condición no cumplida, también se debe deshabilitar el total correspondiente.
                if (status === 'cotizado_parcial' || status === 'facturado_parcial') {
                    let totalStatus = status.replace('parcial', 'total');
                    let totalCheckbox = this.closest('td').querySelector(`input[data-status="${totalStatus}"]`);
                    if (totalCheckbox) {
                        totalCheckbox.checked = false;
                        totalCheckbox.disabled = true;
                    }
                }
                return;
            }
        }

        // Enviar la solicitud de actualización al servidor usando AJAX
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/update_status', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                console.log('Success:', JSON.parse(xhr.responseText));
            } else if (xhr.readyState === 4) {
                console.error('Error:', xhr.responseText);
            }
        };
        xhr.send(JSON.stringify({
            id: this.dataset.id,
            status: this.dataset.status,
            value: isChecked ? 1 : 0,
        }));
    });
});