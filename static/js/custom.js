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



// function initAutoComplete() {
//     if (typeof google === 'undefined' || typeof google.maps === 'undefined') {
//         // Google Maps JavaScript API nie jest jeszcze załadowane, spróbuj ponownie po chwili
//         setTimeout(initAutoComplete, 100);
//         return;
//     }

//     // Google Maps JavaScript API jest załadowane, kontynuuj inicjalizację
//     var inputElement = document.getElementById('id_address');

//     if (inputElement && inputElement instanceof HTMLInputElement) {
//         autocomplete = new google.maps.places.Autocomplete(
//             inputElement,
//             {
//                 types: ['geocode', 'establishment'],
//             }
//         );

//         // Funkcja określająca, co powinno się stać, gdy zostanie wybrane miejsce
//         autocomplete.addListener('place_changed', onPlaceChanged);
//     } else {
//         console.error('Invalid input element');
//     }
// }

// // Wywołaj funkcję initAutoComplete po załadowaniu strony
// document.addEventListener('DOMContentLoaded', initAutoComplete);


// function onPlaceChanged (){
//     var place = autocomplete.getPlace();

//     // User did not select the prediction. Reset the input field or alert()
//     if (!place.geometry){
//         document.getElementById('id_address').placeholder = "Start typing...";
//     }
//     else{
//         console.log('place name=>', place.name)
//     }

//     // get the address components and assign them to the fields
//     var geocoder = new google.maps.Geocoder()
//     var address = document.getElementById('id_address')

//     geocoder.geocode({'address': address}, function(results, status){
//         if(status == google.maps.GeocoderStatus.OK){
//             var latitude = results[0].geometry.location.lat();
//             var longitude = result[0].geometry.location.lng();

//             $('#id_latitude').var(latitude);
//             $('#id_longitude').val(longitude);
//         }
//       })
//     }

//     function initMap() {
//     var input = document.getElementById('id_address');
//     var autocomplete = new google.maps.places.Autocomplete(input);

//     autocomplete.addListener('place_changed', function() {
//         var place = autocomplete.getPlace();

//         console.log('Place:', place);

//         // Sprawdź, czy miejsce zawiera 'address' lub 'formatted_address'
//         var address = place.address || place.formatted_address;

//         if (address) {
//             document.getElementById('id_country').value = getComponent(place, 'country');
//             document.getElementById('id_city').value = getComponent(place, 'locality');
//             document.getElementById('id_latitude').value = place.geometry.location.lat();
//             document.getElementById('id_longitude').value = place.geometry.location.lng();
//         } else {
//             console.error('Invalid place object:', place);
//         }
//     });
// }