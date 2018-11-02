var map = L.map('map').setView([-1.010565, 106.853122], 6);
// L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
// https://api.mapbox.com/styles/v1/hendriprayugo/cj07totii000z2smz7l8b0yz8/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiaGVuZHJpcHJheXVnbyIsImEiOiJjaWlpamthNnUwMHE5dWNrcDlodnAxOGgwIn0.OdKW9hysCK29qvhTAfP3xQ
L.tileLayer('https://api.mapbox.com/styles/v1/hendriprayugo/cj07totii000z2smz7l8b0yz8/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiaGVuZHJpcHJheXVnbyIsImEiOiJjaWlpamthNnUwMHE5dWNrcDlodnAxOGgwIn0.OdKW9hysCK29qvhTAfP3xQ', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
var map2 = L.map('map2').setView([-1.010565, 106.853122], 6);
map2.sync(map);
map.sync(map2);

var aod_gradient = [0, 1, 2, 3, 4, 5, 6];
var rasterObj, image, cursor;

function byteString(n) {
    if (n < 0 || n > 255 || n % 1 !== 0) {
        throw new Error(n + " does not fit in a byte");
    }
    return ("000000000" + n.toString(2)).substr(-8)
}


$(function () {
    $("#datepicker").datepicker();
});

function initpage() {
    select_range_time();
    $('#range-time').change(function () {
        select_range_time();
    });
    $('#datepicker').change(function () {
        select_range_time();
    });
    $('#year').change(function () {
        select_range_time();
    });
    $('#month').change(function () {
        select_range_time();
    });
}

function select_range_time() {
    var data = $('#range-time').val();
    if (data === 'day') {
        $('.d').show();
        $('.m').hide();
        setTimeout(load_raster_daily, 500);
    } else {
        $('.m').show();
        $('.d').hide();
        setTimeout(load_raster_monthly, 500);
    }
}

function reload() {

}

function load_raster_daily() {
    var time = $('#datepicker').val().split('/');
    var dd = time[1];
    var mm = time[0];
    var yyyy = time[2];
    image = new Image;
    image.src = '/raster/daily/' + dd + '-' + mm + '-' + yyyy;
    image.onload = function () {
        rasterObj = decodeImage(image, 'rainbow', [0, 5.5]);
        map.on('moveend move', function (e) {
            try {
                clearTimeout(moveFps)
            } catch (e) {
            }
            doRaster();
        });
        setTimeout(doRaster, 500);
    };
}

function load_raster_monthly() {
    var year = $('#year').val();
    var month = $('#month').val();
    image = new Image;
    image.src = '/raster/monthly/01-' + month + '-' + year;
    image.onload = function () {
        rasterObj = decodeImage(image, 'rainbow', [0, 5.5]);
        map.on('moveend move', function (e) {
            try {
                clearTimeout(moveFps)
            } catch (e) {
            }
            doRaster();
        });
        setTimeout(doRaster, 500);
    };

}

function load_timeseries_monthly(lat, lon, time_start, time_end) {

}

function load_timeseries_daily(lat, lon, time_start, time_end) {

}

function decodeImage(img, color, minmax) {
    var canvas = document.createElement('canvas');
    canvas.setAttribute('width', img.width);
    canvas.setAttribute('height', img.height);
    var ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0, img.width, img.height);
    var im = ctx.getImageData(0, 0, img.width, img.height);
    var imgData = im.data;
    var imInfo = '';
    for (var x = 0; x < imgData.length; x++) {
        if ((x + 1) % 4 === 0) {
            if (imgData[x] === 0)
                break;
            continue;
        }
        if (String.fromCharCode(imgData[x]) === 'x')
            break;
        imInfo = imInfo + String.fromCharCode(imgData[x]);
    }
    var infos = imInfo.split("|");
    var datatype = infos[0];
    var top, bottom, left, right;
    var min = parseFloat(infos[1]);
    var max = parseFloat(infos[2]);
    top = parseFloat(infos[3]);
    bottom = parseFloat(infos[4]);
    left = parseFloat(infos[5]);
    right = parseFloat(infos[6]);
    var colorBar = getColorBar(color);
    var magArr = [];
    var red, green, blue, magVal, magv;
    for (x = 0; x < imgData.length; x++) {
        if ((x + 1) % 4 === 0) {
            red = byteString(imgData[x - 3]);
            green = byteString(imgData[x - 2]);
            blue = byteString(imgData[x - 1]);
            magv = parseInt(red + green + blue, 2);
            magVal = min + (magv / 16777200 * (max - min));
            magArr[((x + 1) / 4) - 1] = magVal;
            var ratio = (magVal - minmax[0]) / (minmax[1] - minmax[0]);
            var col = Math.floor(256 * ratio) + 1;
            if (col > 256)
                col = 256;
            if (col < 0)
                col = 0;
            var colpos = col * 4;
            imgData[x - 3] = colorBar[colpos];
            imgData[x - 2] = colorBar[colpos + 1];
            imgData[x - 1] = colorBar[colpos + 2];
        }
    }
    // $(".legend-value-1").html(minmax[0]);
    // $(".legend-value-2").html((minmax[0] + minmax[1]) / 2);
    // $(".legend-value-3").html(minmax[1]);
    ctx.putImageData(im, 0, 0);
    ctx.clearRect(0, 0, img.width, 5);
    var strPng = canvas.toDataURL();
    var decodedImage = new Image;
    decodedImage.src = strPng;
    return {
        decodedImage: decodedImage,
        type: datatype,
        magArray: [],
        minVal: min,
        maxVal: max,
        width: img.width,
        height: img.height,
        bounding: {
            top: top,
            bottom: bottom,
            left: left,
            right: right
        }
    };

}

function getColorBar(color) {
    var pals = {
        "gas": {
            "colors": ["#052A2B", "#FBF9D8", "#E68D70", "#9B0080", "#190A54", "#150778"],
            "colorsstop": [0, 0.2, 0.4, 0.6, 0.8, 1]
        },
        "temp": {
            "colors": ["#512728", "#BC2A97", "#44D2D5", "#F6FA3A", "#DD4428", "#5B1C42", "#0a0d70"],
            "colorsstop": [0, 0.2, 0.4, 0.6, 0.8, 0.9, 1]
        },
        "rainbow": {
            "colors": ["#0000D4", "#04d0d3", "#01ba04", "#cece00", "#DD0000", "#4B0086", "#260193"],
            "colorsstop": [0, 0.2, 0.25, 0.35, 0.8, 0.9, 1]
        },
        "cloud": {
            "colors": ["#ff5800", "#ff5800", "#222", "#fff"],
            "colorsstop": [0, 0.35, 0.35, 1]
        }
    };
    var xcol = pals[color];
    var cvs = document.createElement("canvas");
    cvs.setAttribute("width", 256);
    cvs.setAttribute("height", 1);
    var ctx = cvs.getContext("2d");
    ctx.lineWidth = 10;
    var grad = ctx.createLinearGradient(0, 0, 256, 1);
    for (var x = 0; x < xcol.colors.length; x++) {
        grad.addColorStop(xcol.colorsstop[x] / xcol.colorsstop[xcol.colors.length - 1], xcol.colors[x]);
    }
    ctx.strokeStyle = grad;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(256, 0);
    ctx.stroke();
    var colorBar = ctx.getImageData(0, 0, cvs.width, cvs.height).data;
    $(".legend-color").attr("src", cvs.toDataURL());
    console.log(cvs.toDataURL());
    return (colorBar);
}

function doRaster() {
    var canvas = document.getElementById("cvs-raster");
    canvas.setAttribute("height", $('#map').height());
    canvas.setAttribute("width", $('#map').width());
    var ctx = canvas.getContext("2d");
    var xy1 = map.latLngToContainerPoint([rasterObj.bounding.top, rasterObj.bounding.left]);
    var xy2 = map.latLngToContainerPoint([rasterObj.bounding.bottom, rasterObj.bounding.right]);
    var mapx = xy1.x;
    var mapy = xy1.y;
    var scaledwidth = xy2.x - xy1.x;
    var originalwidth = rasterObj.width;
    var xscale = originalwidth / scaledwidth;
    var scaledheight = Math.abs(xy1.y - xy2.y);
    var originalheight = rasterObj.height;
    var yscale = originalheight / scaledheight;
    var xcrop = (function () {
        if (xy1.x > 0) {
            return 0;
        } else {
            return Math.abs(mapx * xscale);
        }
    })();
    var ycrop = (function () {
        if (xy1.y > 0) {
            return 0;
        } else {
            return Math.abs(mapy * yscale);
        }
    })();
    var widthcrop = (function () {
        if (xy2.x < canvas.width) {
            return originalwidth;
        } else {
            return (scaledwidth - (xy2.x - canvas.width)) * xscale;
        }
    })();
    var heightcrop = (function () {
        if (xy2.y < canvas.height) {
            return originalheight;
        } else {
            return (scaledheight - (xy2.y - canvas.height)) * yscale;
        }
    })();
    mapx = (xcrop !== 0) ? 0 : mapx;
    mapy = (ycrop !== 0) ? 0 : mapy;
    scaledwidth = scaledwidth - (scaledwidth - (widthcrop / xscale));
    scaledheight = scaledheight - (scaledheight - (heightcrop / yscale));
    ctx.drawImage(rasterObj.decodedImage, xcrop, ycrop, widthcrop, heightcrop, mapx, mapy, scaledwidth, scaledheight);
    var canvasData = ctx.getImageData(0, 0, $("#map").width(), $("#map").height());
    var pix = canvasData.data;
    for (var i = 0, n = pix.length; i < n; i += 4) {
        if (pix[i + 3] < 50 && pix[i + 3] !== 0) {
            pix[i + 3] = 0;
        } else if (pix[i + 3] !== 0) {
            pix[i + 3] = 255;
        }
    }
    ctx.putImageData(canvasData, 0, 0);
}

map2.on('click', function (e) {
    try {
        map2.removeLayer(cursor)
    } catch (e) {}
    var latlng = map2.mouseEventToLatLng(e.originalEvent);
    console.log(latlng.lat + ', ' + latlng.lng);
    cursor = L.marker([latlng.lat, latlng.lng]).addTo(map2);
});

initpage();