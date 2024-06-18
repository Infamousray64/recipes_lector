document.getElementById('downloadForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Previene el envío tradicional del formulario

    // Obtener los valores de mes, año y estatus desde los elementos de entrada
    var mes = document.getElementById('mes').value;
    var ano = document.getElementById('ano').value;

    // Construir la URL con parámetros de consulta para mes y año
    var url = `/download?mes=${mes}&ano=${ano}`;

    fetch(url, {
        method: 'GET',
    })
    .then(response => response.blob())
    .then(blob => {
        // Crear un enlace temporal para descargar el archivo
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = downloadUrl;
        // Especificar el nombre del archivo para descargar
        a.download = `resultados_${mes}_${ano}.xls`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        alert('Archivo Excel descargado exitosamente ✅');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Hubo un error al descargar el archivo ❌');
    });
});