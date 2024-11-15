let autocomplete;

function initAutoComplete() {
    var inputElement = document.getElementById('id_address');

    if (inputElement && inputElement instanceof HTMLInputElement) {
        autocomplete = new google.maps.places.Autocomplete(
            inputElement,
            {
                types: ['geocode', 'establishment'],
            }
        );

        // Funkcja określająca, co powinno się stać, gdy zostanie wybrane miejsce
        autocomplete.addListener('place_changed', onPlaceChanged);
    } else {
        console.error('Invalid input element');
    }
}

function onPlaceChanged() {
    var place = autocomplete.getPlace();

    // Uzupełnij pola formularza na podstawie danych z Google Places API
    document.getElementById('id_country').value = getComponentValue(place.address_components, 'country');
    document.getElementById('id_city').value = getComponentValue(place.address_components, 'locality');
    document.getElementById('id_latitude').value = place.geometry.location.lat();
    document.getElementById('id_longitude').value = place.geometry.location.lng();
}

function getComponentValue(components, type) {
    for (var i = 0; i < components.length; i++) {
        for (var j = 0; j < components[i].types.length; j++) {
            if (components[i].types[j] === type) {
                return components[i].long_name;
            }
        }
    }
    return '';
}

// Wywołaj funkcję initAutoComplete po załadowaniu strony
document.addEventListener('DOMContentLoaded', initAutoComplete);





