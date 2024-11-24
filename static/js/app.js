
        // AJAX para analizar imagen subida
        $('#uploadForm').submit(function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            showLoading();

            $.ajax({
                url: '/analyze',
                type: 'POST',
                data: formData,
                contentType: false,
                processData: false,
                success: function (response) {
                    hideLoading();
                    $('#results').removeClass('hidden');
                    $('#resultImage').attr('src', 'data:image/png;base64,' + response.image);
                },
                error: function (xhr) {
                    hideLoading();
                    $('#error')
                        .removeClass('hidden')
                        .text(xhr.responseJSON?.error || 'An error occurred');
                }
            });
        });

        function analyzeExisting(filename) {
    showLoading();
    const formData = new FormData();
    formData.append('existing_file', filename);

    $.ajax({
        url: '/analyze',
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function (response) {
            hideLoading();
            $('#results').removeClass('hidden');
            $('#resultImage').attr('src', 'data:image/png;base64,' + response.image); // Cambia esto según la respuesta del servidor
            $('#resultImage').css('display', 'block'); // Muestra la imagen
        },
        error: function (xhr) {
            hideLoading();
            $('#error')
                .removeClass('hidden')
                .text(xhr.responseJSON?.error || 'An error occurred');
        }
    });
    console.log("Analizando imagen:", filename);
}
// Supongamos que tienes una función que maneja la respuesta después del análisis
function handleAnalysisResponse(response) {
    console.log('Analizando imagen: caramora.jpg');

    // Verifica si la respuesta contiene una URL válida para la imagen
    if (response.imageUrl) {
        // Actualiza el src de la imagen en el div de resultados
        const resultImage = document.getElementById('resultImage');
        resultImage.src = response.imageUrl;

        // Muestra la imagen
        resultImage.style.display = 'block'; // Muestra la imagen

        // Muestra la sección de resultados
        const resultsSection = document.getElementById('results');
        resultsSection.classList.remove('hidden');
    } else {
        // Maneja el error si no hay URL
        const errorDiv = document.getElementById('error');
        errorDiv.textContent = 'Error al cargar la imagen de análisis.';
        errorDiv.classList.remove('hidden');
    }
}

        // Mostrar/Ocultar el indicador de carga
        function showLoading() {
            $('#loading').removeClass('hidden');
        }

        function hideLoading() {
            $('#loading').addClass('hidden');
        }

        function previewImage(event) {
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        const imgElement = document.getElementById('resultImage');
        imgElement.src = e.target.result;
        imgElement.style.display = 'block'; // Mostrar la imagen
        document.getElementById('results').classList.remove('hidden'); // Mostrar sección de resultados
    };

    if (file) {
        reader.readAsDataURL(file);
    }
}

function handleFormSubmit(event) {
    event.preventDefault(); // Prevenir el envío del formulario
    document.getElementById('loading').classList.remove('hidden'); // Mostrar el spinner
    document.getElementById('error').classList.add('hidden'); // Ocultar errores

    // Simular un análisis de imagen (reemplaza con tu lógica real)
    setTimeout(() => {
        document.getElementById('loading').classList.add('hidden'); // Ocultar el spinner
        // Aquí podrías manejar la respuesta del análisis
        // Si hay un error, muestra el mensaje de error
        // document.getElementById('error').classList.remove('hidden'); // Descomentar para mostrar error
    }, 2000); // Simulación de un análisis que dura 2 segundos
}
function deleteImage(filename) {
    if (confirm('¿Estás seguro de que deseas eliminar esta imagen?')) {
        $.ajax({
            url: '/delete', // Cambia esta URL según tu configuración
            type: 'POST',
            data: { filename: filename },
            success: function(response) {
                // Aquí puedes manejar la respuesta después de la eliminación
                alert('Imagen eliminada con éxito');
                location.reload(); // Recargar la página para ver los cambios
            },
            error: function(xhr) {
                alert('Ocurrió un error al intentar eliminar la imagen: ' + xhr.responseJSON?.error || 'Error desconocido');
            }
        });
    }
}
function confirmDelete(filename) {
    Swal.fire({
        title: '¿Estás seguro?',
        text: "¡Esta acción no se puede deshacer!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            // Crear un formulario para eliminar la imagen
            const formData = new FormData();
            formData.append('filename', filename);

            // Hacer una solicitud AJAX para eliminar la imagen
            fetch('/delete', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire('Eliminado', 'La imagen ha sido eliminada.', 'success');
                    // Eliminar la imagen del DOM
                    document.querySelector(`img[src*="${filename}"]`).parentElement.remove();
                } else {
                    Swal.fire('Error', data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire('Error', 'Ocurrió un error al eliminar la imagen.', 'error');
            });
        }
    });
}

