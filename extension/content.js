//const videoElement = document.querySelector('video'); // Находим элемент <video>.
//videoElement.addEventListener('click', (event) => { // Добавляем обработчик событий клика на элементе <video>.
//    const rect = videoElement.getBoundingClientRect(); // Получаем координаты прямоугольника, охватывающего элемент <video>.
//    const x = event.clientX - rect.left; // Вычисляем относительную координату X клика относительно элемента <video>.
//    const y = event.clientY - rect.top; // Вычисляем относительную координату Y клика относительно элемента <video>.
//    const timestamp = videoElement.currentTime; // Получаем текущее время воспроизведения видео.
//    const videoId = window.location.search.split('v=')[1]; // Извлекаем идентификатор видео из URL-адреса страницы YouTube.
////    const isPaused = videoElement.paused; // Значение true, если видео на паузе.
////    const videoWidth = videoElement.videoWidth; // Ширина видео в пикселях.
////    const videoHeight = videoElement.videoHeight; // Высота видео в пикселях.
////    const videoQuality = "1080p"; // Разрешение видео.
////    const playbackRate = videoElement.playbackRate; // Скорость воспроизведения.
////    const videoDuration = videoElement.duration; // Длительность видео в секундах.
////    const isPaused = videoElement.paused; // Значение true, если видео на паузе.
////    const videoSource = String(videoElement.src); // URL-адрес источника видео.
//
//    fetch('http://127.0.0.1:8000/click/', { // Отправляем HTTP-запрос на указанный URL.
////    fetch('http://127.0.0.1:8080/click/', { // Или используем порт нашего прокси-сервера
//        method: 'POST', // Используем метод POST.
//        headers: { // Устанавливаем заголовки.
//            'Content-Type': 'application/json' // Указываем тип содержимого как application/json.
//        },
//        body: JSON.stringify({ // Преобразуем данные в формат JSON и отправляем на сервер.
//            x: x, // Добавляем координату X клика.
//            y: y, // Добавляем координату Y клика.
//            timestamp: timestamp, // Добавляем временную метку.
//            videoId: videoId // Добавляем идентификатор видео.
//        })
//    });
//});



const videoElement = document.querySelector('video'); // Находим элемент <video>.

let isVideoPaused = false; // Инициализируем переменную, отвечающую за статус паузы видео.

videoElement.addEventListener('play', () => { // Добавляем обработчик события play на видео.
    isVideoPaused = false; // Устанавливаем статус паузы видео в false.
    console.log('*****1***Video paused:', isVideoPaused); // Выводим в консоль статус паузы видео.
});

videoElement.addEventListener('pause', () => { // Добавляем обработчик события pause на видео.
    isVideoPaused = true; // Устанавливаем статус паузы видео в true.
    console.log('*****2***Video paused:', isVideoPaused); // Выводим в консоль статус паузы видео.
});

let clickTimer; // Инициализируем переменную для таймера.

videoElement.addEventListener('click', (event) => { // Добавляем обработчик события клика на видео.
    if (isVideoPaused) { // Проверяем, находится ли видео на паузе.
        if (!clickTimer) { // Проверяем, установлен ли таймер клика.
            clickTimer = setTimeout(() => { // Устанавливаем таймер клика на определенный промежуток времени.
                const rect = videoElement.getBoundingClientRect(); // Получаем прямоугольник, охватывающий элемент видео.
                const x = event.clientX - rect.left; // Вычисляем относительную координату X клика относительно элемента <video>.
                const y = event.clientY - rect.top; // Вычисляем относительную координату Y клика относительно элемента <video>.
                const timestamp = videoElement.currentTime; // Получаем текущее время воспроизведения видео.
                const videoId = window.location.search.split('v=')[1]; // Извлекаем идентификатор видео из URL-адреса.

                fetch('http://127.0.0.1:8000/click/', { // Отправляем POST-запрос на указанный URL.
                    method: 'POST', // Используем метод POST.
                    headers: { // Устанавливаем заголовки.
                        'Content-Type': 'application/json' // Указываем тип содержимого как application/json.
                    },
                    body: JSON.stringify({ // Преобразуем данные в формат JSON и отправляем на сервер.
                        x: x, // Добавляем координату X клика.
                        y: y, // Добавляем координату Y клика.
                        timestamp: timestamp, // Добавляем временную метку.
                        videoId: videoId // Добавляем идентификатор видео.
                    })
                });

                clickTimer = null; // Сбрасываем таймер.
            }, 1000); // Устанавливаем задержку в 1 секунду.
        }
    }
});




//const videoElement = document.querySelector('video'); // Находим элемент <video>.
//
//videoElement.addEventListener('click', (event) => { // Добавляем обработчик события клика на элемент <video>.
//    const rect = videoElement.getBoundingClientRect(); // Получаем координаты прямоугольника, охватывающего элемент <video>.
//    const x = event.clientX - rect.left; // Вычисляем относительную координату X клика относительно элемента <video>.
//    const y = event.clientY - rect.top; // Вычисляем относительную координату Y клика относительно элемента <video>.
//    const timestamp = videoElement.currentTime; // Получаем текущее время воспроизведения видео.
//    const videoId = window.location.search.split('v=')[1]; // Извлекаем идентификатор видео из URL-адреса страницы.
//
//    const data = { // Формируем объект с данными о клике.
//        x: x, // Добавляем координату X клика.
//        y: y, // Добавляем координату Y клика.
//        timestamp: timestamp, // Добавляем временную метку.
//        videoId: videoId // Добавляем идентификатор видео.
//    };
//
//    fetch('http://127.0.0.1:8000/click/', { // Отправляем POST-запрос на указанный URL.
//        method: 'POST', // Используем метод POST.
//        headers: { // Устанавливаем заголовки запроса.
//            'Content-Type': 'application/json' // Указываем тип содержимого как application/json.
//        },
//        body: JSON.stringify(data) // Преобразуем данные в формат JSON и отправляем на сервер.
//    });
//});



