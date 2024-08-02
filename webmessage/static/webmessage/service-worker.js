self.addEventListener('install', function(event) {
    // 서비스 워커 설치 시 활성화
    self.skipWaiting();
});

self.addEventListener('activate', function(event) {
    // 활성화 단계에서 기존 클라이언트를 제어하도록 설정
    event.waitUntil(
        clients.claim()
    );
});

self.addEventListener('push', function(event) {
    let data;

    try {
        data = event.data.json();
    } catch (e) {
        data = { title: 'Notification', body: event.data.text() };
    }

    const options = {
        body: data.body,
        icon: data.icon || 'default-icon-url',
        badge: data.badge || 'default-badge-url',
        image: data.image,
        data: {
            url: data.url // 알림 클릭 시 이동할 URL을 포함합니다.
        }
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url || 'https://default-url.com') // 알림 클릭 시 이동할 기본 URL
    );
});
