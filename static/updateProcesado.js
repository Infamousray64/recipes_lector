document.querySelectorAll('.status-checkbox').forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        var status = this.dataset.status;
        var isChecked = this.checked;
        var enProcesoCheckbox = this.closest('td').querySelector('input[data-status="en_proceso"]');
        var cotizadoParcialCheckbox = this.closest('td').querySelector('input[data-status="cotizado_parcial"]');
        var cotizadoTotalCheckbox = this.closest('td').querySelector('input[data-status="cotizado_total"]');
        var facturadoParcialCheckbox = this.closest('td').querySelector('input[data-status="facturado_parcial"]');
        var facturadoTotalCheckbox = this.closest('td').querySelector('input[data-status="facturado_total"]');

        // Verificar condiciones para cotizado parcial o total
        if ((status === 'cotizado_parcial' || status === 'cotizado_total') && isChecked && !enProcesoCheckbox.checked) {
            alert('Para marcar como cotizado, primero debe estar en proceso.');
            this.checked = false; // Desmarcar porque no cumple la condición previa
            return;
        }

        // Verificar condiciones para facturado parcial o total
        if ((status === 'facturado_parcial' || status === 'facturado_total') && isChecked && !(cotizadoParcialCheckbox.checked || cotizadoTotalCheckbox.checked)) {
            alert('Para marcar como facturado, primero debe estar cotizado.');
            this.checked = false; // Desmarcar porque no cumple la condición previa
            return;
        }

        // Nueva lógica para evitar seleccionar otro estatus parcial o total si ya se tiene uno marcado
        var anyPartialChecked = cotizadoParcialCheckbox.checked || facturadoParcialCheckbox.checked;
        var anyTotalChecked = cotizadoTotalCheckbox.checked || facturadoTotalCheckbox.checked;

        if (isChecked) {
            if (anyPartialChecked && status.includes('total')) {
                alert('No puede seleccionar un estado total si ya tiene un estado parcial marcado.');
                this.checked = false; // Desmarcar porque no cumple la nueva condición
                return;
            } else if (anyTotalChecked && status.includes('parcial')) {
                alert('No puede seleccionar un estado parcial si ya tiene un estado total marcado.');
                this.checked = false; // Desmarcar porque no cumple la nueva condición
                return;
            }
        }

        // Deshabilitar el otro cotizado si uno es marcado
        if (status === 'cotizado_parcial' && isChecked) {
            cotizadoTotalCheckbox.disabled = true;
        } else if (status === 'cotizado_total' && isChecked) {
            cotizadoParcialCheckbox.disabled = true;
        } else if (status === 'cotizado_parcial' && !isChecked) {
            cotizadoTotalCheckbox.disabled = false;
        } else if (status === 'cotizado_total' && !isChecked) {
            cotizadoParcialCheckbox.disabled = false;
        }

        // Deshabilitar el otro facturado si uno es marcado
        if (status === 'facturado_parcial' && isChecked) {
            facturadoTotalCheckbox.disabled = true;
        } else if (status === 'facturado_total' && isChecked) {
            facturadoParcialCheckbox.disabled = true;
        } else if (status === 'facturado_parcial' && !isChecked) {
            facturadoTotalCheckbox.disabled = false;
        } else if (status === 'facturado_total' && !isChecked) {
            facturadoParcialCheckbox.disabled = false;
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
        var clickedTime = new Date().toISOString();
        xhr.send(JSON.stringify({
            id: this.dataset.id,
            status: this.dataset.status,
            value: isChecked ? 1 : 0,
            clickedTime: clickedTime, // Incluir la hora actual en la solicitud
        }));
    });
});