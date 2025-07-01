// static/js/notifications.js
const eventSource = new EventSource('/api/notifications/');
eventSource.onmessage = (e) => {
    Toastify({
        text: `Nouvelle absence: ${e.data.employee_name}`,
        duration: 5000
    }).showToast();
};
