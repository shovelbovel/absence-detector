document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('sendMessageForm');
    form.addEventListener('submit', function (event) {
        let valid = true;
        // Validation simple
        form.querySelectorAll('select, input, textarea').forEach(field => {
            if (field.hasAttribute('required') && !field.value.trim()) {
                field.classList.add('is-invalid');
                valid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        if (!valid) {
            event.preventDefault();
            event.stopPropagation();
        }
    });
});

$(document).ready(function() {
    // Initialiser Select2 sur le sélecteur de destinataire
    $('#recipient-select').select2({
        theme: 'bootstrap4',
        placeholder: 'Sélectionnez un destinataire...',
        width: '100%'
    });

    // Empêcher la soumission si aucun destinataire n'est sélectionné
    $('form').on('submit', function(e) {
        if (!$('#recipient-select').val()) {
            e.preventDefault();
            alert('Veuillez sélectionner un destinataire');
        }
    });
});