console.log('main.js is loaded');

if ('serviceWorker' in navigator && 'PushManager' in window) {
    navigator.serviceWorker.register('./service-worker.js').then(function(swReg) {
        console.log('Service Worker Registered', swReg);

        // 새로운 서비스 워커가 설치될 때 대체하도록 설정
        swReg.onupdatefound = function() {
            const installingWorker = swReg.installing;
            installingWorker.onstatechange = function() {
                if (installingWorker.state === 'installed') {
                    if (navigator.serviceWorker.controller) {
                        console.log('New content is available; please refresh.');
                        // 새 서비스 워커를 즉시 활성화
                        installingWorker.postMessage({ action: 'skipWaiting' });
                    } else {
                        console.log('Content is cached for offline use.');
                    }
                }
            };
        };

        swReg.pushManager.getSubscription().then(function(subscription) {
            if (subscription === null) {
                // 구독 정보가 없으면 새로운 구독을 요청
                console.log('No subscription found, requesting new subscription');
                swReg.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(window.vapidPublicKey)  // 여기서 VAPID 공개 키를 사용합니다.
                }).then(function(subscription) {
                    console.log('User is subscribed:', subscription);
                    displaySubscriptionInfo(subscription);
                }).catch(function(error) {
                    console.error('Failed to subscribe the user: ', error);
                });
            } else {
                console.log('User is already subscribed:', subscription);
                displaySubscriptionInfo(subscription);
            }
        });
    }).catch(function(error) {
        console.error('Service Worker Error', error);
    });
} else {
    console.warn('Push messaging is not supported');
}

function displaySubscriptionInfo(subscription) {
    const subscriptionInfo = document.getElementById('subscription-info');
    subscriptionInfo.textContent = 'Subscription: ' + JSON.stringify(subscription);
    console.log('Subscription:', subscription);
}


function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}
