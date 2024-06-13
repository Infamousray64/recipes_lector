document.getElementById('downloadButton').addEventListener('click', function() {
    fetch('/download', {
        method: 'GET',
    })
    .then(response => response.blob())
    .then(blob => {
        // Crear un enlace temporal para descargar el archivo
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        // Especificar el nombre del archivo para descargar
        a.download = 'resultados.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        alert('Archivo Excel descargado exitosamente ✅');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Hubo un error al descargar el archivo ❌');
    });
});