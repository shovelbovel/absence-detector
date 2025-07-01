// static/js/analytics.js
function renderCharts(data) {
    new Chart(document.getElementById('activity-chart'), {
        type: 'bar',
        data: {
            labels: data.hours,
            datasets: [{
                label: 'Activité par heure',
                data: data.counts,
                backgroundColor: 'rgba(75, 192, 192, 0.6)'
            }]
        }
    });
}