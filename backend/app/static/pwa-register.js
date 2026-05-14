/**
 * PWA Registration Script
 * Only active on mobile devices (width < 768px)
 */

function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/static/sw.js')
                .then((registration) => {
                    console.log('SW registered: ', registration);
                })
                .catch((registrationError) => {
                    console.log('SW registration failed: ', registrationError);
                });
        });
    }
}

// Check if mobile width
console.log("PWA Check: Width is " + window.innerWidth);
if (window.matchMedia('(max-width: 767px)').matches) {
    console.log("PWA Check: Mobile detected, registering...");
    registerServiceWorker();
} else {
    console.log("PWA Check: Desktop detected, skipping registration.");
}
