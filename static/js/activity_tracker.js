let inactivityTimeout;
const INACTIVITY_DELAY = 300000; // 5 minutes en millisecondes
const WARNING_DELAY = 240000; // 4 minutes

function resetInactivityTimer() {
    clearTimeout(inactivityTimeout);
    
    // Envoyer une requête au serveur pour enregistrer l'activité
    fetch('/activity/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            activity_type: 'mouse'  // ou 'keyboard' selon l'événement
        })
    });
    
    // Redémarrer le timer
    inactivityTimeout = setTimeout(warnInactivity, WARNING_DELAY);
}

function warnInactivity() {
    // Afficher un avertissement
    alert("Vous semblez inactif. Votre statut sera changé en 'Absent' dans 1 minute si aucune activité n'est détectée.");
    
    // Définir un dernier délai avant de marquer comme absent
    inactivityTimeout = setTimeout(markAbsent, 60000);
}

function markAbsent() {
    // Envoyer une requête pour changer le statut
    fetch('/status/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            status: 'absent'
        })
    });
}

function changeStatus(newStatus) {
    fetch('/status/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            status: newStatus
        })
    }).then(response => {
        document.getElementById('current-status').textContent = newStatus;
    });
}

// Détecteurs d'événements
document.addEventListener('mousemove', resetInactivityTimer);
document.addEventListener('keypress', resetInactivityTimer);

// Fonction utilitaire pour récupérer le cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialiser le timer au chargement
resetInactivityTimer();
class ActivityMonitor {
    constructor() {
        this.inactivityTimeout = null;
        this.warningTimeout = null;
        this.INACTIVITY_LIMIT = 300000; // 5 minutes
        this.WARNING_TIME = 240000; // 4 minutes
        
        this.initEvents();
        this.resetTimer();
    }
    
    initEvents() {
        ['mousemove', 'keydown', 'scroll', 'click'].forEach(event => {
            document.addEventListener(event, this.resetTimer.bind(this));
        });
    }
    
    resetTimer() {
        clearTimeout(this.inactivityTimeout);
        clearTimeout(this.warningTimeout);
        
        this.sendActivity();
        
        this.warningTimeout = setTimeout(this.showWarning.bind(this), this.WARNING_TIME);
        this.inactivityTimeout = setTimeout(this.markInactive.bind(this), this.INACTIVITY_LIMIT);
    }
    
    showWarning() {
        if (confirm("Vous semblez inactif. Cliquez sur OK pour rester connecté.")) {
            this.resetTimer();
        }
    }
    
    markInactive() {
        fetch('/api/status/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({ status: 'inactive' })
        }).then(() => {
            window.location.reload();
        });
    }
    
    sendActivity() {
        fetch('/api/activity/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCsrfToken()
            }
        });
    }
    
    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

new ActivityMonitor();