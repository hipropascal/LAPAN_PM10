var map = L.map('map').setView([-1.010565, 106.853122], 6);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

$(function () {
    $("#datepicker").datepicker();
});

function initpage() {
    select_range_time();
    $('#range-time').change(function () {
        select_range_time();
    });
}

function select_range_time() {
    var data = $('#range-time').val();
    if (data === 'day') {
        $('.d').show();
        $('.m').hide();
    } else {
        $('.m').show();
        $('.d').hide();
    }
}

initpage();