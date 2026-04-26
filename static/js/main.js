// Shared logic for every page.

// Theme 
const applyTheme = t => {
    document.querySelector('html').setAttribute('data-theme', t);
    localStorage.setItem('tf-theme', t);
};
applyTheme(localStorage.getItem('tf-theme') || 'light');

// Asset base path
const assetBase = '/static/assets/';

// Modal helper
window.bloomModal = {
    open(backdropSel, modalSel) {
        $(backdropSel + ', ' + modalSel).addClass('visible');
        $('body').css('overflow', 'hidden');
    },
    close(backdropSel, modalSel) {
        $(backdropSel + ', ' + modalSel).removeClass('visible');
        $('body').css('overflow', '');
    }
};

// Shared input validators 
window.bloomValidate = {

    // Name fields — letters, spaces, apostrophes, commas, periods, hyphens
    NAME_PATTERN: /^[a-zA-ZÀ-ÿ\s'.,\-]+$/,
    sanitizeName(value) {
        return value.replace(/[^a-zA-ZÀ-ÿ\s'.,\-]/g, '');
    },
    isValidName(value) {
        return value.trim().length > 0 && this.NAME_PATTERN.test(value.trim());
    },

    // Username - letters, digits, @, ., +, -, _ (Django standard)
    USERNAME_PATTERN: /^[\w.@+\-]+$/,
    isValidUsername(value) {
        return value.trim().length > 0 && this.USERNAME_PATTERN.test(value.trim());
    },

    // Email
    EMAIL_PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    isValidEmail(value) {
        return this.EMAIL_PATTERN.test(value.trim());
    },

    // Free text - just checks min/max length
    isValidLength(value, min, max) {
        const len = value.trim().length;
        if (min !== undefined && len < min) return false;
        if (max !== undefined && len > max) return false;
        return true;
    },

    // Number - checks min/max value
    isValidNumber(value, min, max) {
        const n = parseFloat(value);
        if (isNaN(n)) return false;
        if (min !== undefined && n < min) return false;
        if (max !== undefined && n > max) return false;
        return true;
    },

    // Password - any char, enforces minLength on register
    isValidPassword(value, minLength) {
        return value.length >= (minLength || 1);
    }
};

$(function () {

    // Theme toggle
    $('#themeToggle').on('click', function () {
        applyTheme(document.querySelector('html').getAttribute('data-theme') === 'light' ? 'dark' : 'light');
    });

    // Navbar scroll state
    const $navbar      = $('#navbar');
    const $toggler     = $('.navbar-toggler');
    const $navCollapse = $('#navLinks');

    $(window).on('scroll', function () {
        $navbar.toggleClass('scrolled', $(window).scrollTop() > 10);
    });

    // Active nav link
    const path = location.pathname.replace(/\/$/, '') || '/';
    $('.nav-link').each(function () {
        const href = $(this).attr('href');
        if (!href) return;
        const hrefPath = href.split('?')[0].replace(/\/$/, '') || '/';
        if (hrefPath === path) $(this).addClass('active');
    });

    // Navbar mobile collapse sync
    $toggler.on('click', function () {
        setTimeout(function () {
            $toggler.attr('aria-expanded', String($navCollapse.hasClass('show')));
        }, 50);
    });
    $('#navLinks .nav-link').on('click', function () {
        $navCollapse.collapse('hide');
        $toggler.attr('aria-expanded', 'false');
    });
    $(document).on('click', function (e) {
        if ($navbar.length && !$(e.target).closest('#navbar').length) {
            $navCollapse.collapse('hide');
            $toggler.attr('aria-expanded', 'false');
        }
    });

    // Animated counter
    function animateCounter(el, target) {
        const step  = target / (1200 / 16);
        let   cur   = 0;
        const timer = setInterval(function () {
            cur += step;
            if (cur >= target) {
                $(el).text(target.toLocaleString());
                clearInterval(timer);
            } else {
                $(el).text(Math.floor(cur).toLocaleString());
            }
        }, 16);
    }

    $('.stat-item_value').each(function () {
        const raw = parseInt($(this).text().replace(/,/g, '')) || 0;
        if (raw > 0) {
            $(this).text('0');
            animateCounter(this, raw);
        }
    });

    // Weather widget
    function wi(name) {
        return '<img src="' + assetBase + 'icons/' + name + '.png" class="weather-icon-img" alt="' + name + '" />';
    }

    const WMO_MAP = {
        0:  { icon: wi('weather-clear'),         desc: 'Clear sky'                  },
        1:  { icon: wi('weather-mainly-clear'),  desc: 'Mainly clear'               },
        2:  { icon: wi('weather-partly-cloudy'), desc: 'Partly cloudy'              },
        3:  { icon: wi('weather-overcast'),      desc: 'Overcast'                   },
        45: { icon: wi('weather-fog'),           desc: 'Fog'                        },
        48: { icon: wi('weather-fog'),           desc: 'Icy fog'                    },
        51: { icon: wi('weather-drizzle'),       desc: 'Light drizzle'              },
        53: { icon: wi('weather-drizzle'),       desc: 'Moderate drizzle'           },
        55: { icon: wi('weather-drizzle'),       desc: 'Dense drizzle'              },
        61: { icon: wi('weather-rain'),          desc: 'Slight rain'                },
        63: { icon: wi('weather-rain'),          desc: 'Moderate rain'              },
        65: { icon: wi('weather-rain'),          desc: 'Heavy rain'                 },
        71: { icon: wi('weather-snow'),          desc: 'Slight snow'                },
        73: { icon: wi('weather-snow'),          desc: 'Moderate snow'              },
        75: { icon: wi('weather-snow'),          desc: 'Heavy snow'                 },
        77: { icon: wi('weather-snow-grains'),   desc: 'Snow grains'                },
        80: { icon: wi('weather-showers'),       desc: 'Slight showers'             },
        81: { icon: wi('weather-showers'),       desc: 'Moderate showers'           },
        82: { icon: wi('weather-showers'),       desc: 'Violent showers'            },
        85: { icon: wi('weather-snow-showers'),  desc: 'Snow showers'               },
        86: { icon: wi('weather-snow-showers'),  desc: 'Heavy snow showers'         },
        95: { icon: wi('weather-thunderstorm'),  desc: 'Thunderstorm'               },
        96: { icon: wi('weather-thunderstorm'),  desc: 'Thunderstorm w/ hail'       },
        99: { icon: wi('weather-thunderstorm'),  desc: 'Thunderstorm w/ heavy hail' },
    };

    function showWeatherError(msg) {
        $('#weatherLoading').removeClass('visible');
        $('#weatherError').text(msg).addClass('visible');
        $('#weatherRefresh').css('display', 'none');
    }

    async function fetchWeather(city) {
        if (!city) return;
        $('#weatherDisplay').removeClass('visible');
        $('#weatherError').removeClass('visible');
        $('#weatherPlaceholder').hide();
        $('#weatherLoading').addClass('visible');

        try {
            const geo = await fetch(
                'https://geocoding-api.open-meteo.com/v1/search?name=' +
                encodeURIComponent(city) + '&count=1&language=en&format=json'
            );
            if (!geo.ok) { showWeatherError('Geocoding request failed.'); return; }

            const geoData = await geo.json();
            if (!geoData.results?.length) { showWeatherError('"' + city + '" not found.'); return; }

            const { latitude, longitude, name, country_code } = geoData.results[0];
            const params = new URLSearchParams({
                latitude, longitude,
                current: 'temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,visibility,weather_code',
                wind_speed_unit: 'kmh',
                timezone: 'auto',
            });

            const wx  = await (await fetch('https://api.open-meteo.com/v1/forecast?' + params)).json();
            const cur = wx.current;
            const wmo = WMO_MAP[cur.weather_code] || { icon: wi('weather-clear'), desc: 'Unknown' };

            $('#weatherIconDisplay').html(wmo.icon);
            $('#weatherTemp').text(Math.round(cur.temperature_2m) + '°C');
            $('#weatherCity').text(name + ', ' + country_code);
            $('#weatherDesc').text(wmo.desc);
            $('#weatherFeelsLike').text(Math.round(cur.apparent_temperature) + '°C');
            $('#weatherHumidity').text(cur.relative_humidity_2m + '%');
            $('#weatherWind').text(Math.round(cur.wind_speed_10m) + ' km/h');
            $('#weatherVisibility').text(cur.visibility != null ? (cur.visibility / 1000).toFixed(1) + ' km' : 'N/A');
            $('#weatherLoading').removeClass('visible');
            $('#weatherDisplay').addClass('visible');
            $('#weatherRefresh').css('display', 'flex');

        } catch (err) {
            showWeatherError(err.message);
        }
    }

    $('#weatherForm').on('submit', function (e) {
        e.preventDefault();
        fetchWeather($('#weatherInput').val().trim());
    });
    $('#weatherRefresh').on('click', function () {
        fetchWeather($('#weatherInput').val().trim());
    });

});