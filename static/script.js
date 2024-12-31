function startClock() {
    setInterval(() => {
        const now = new Date();
        const clock = document.getElementById("clock");
        clock.innerText = now.toLocaleTimeString();
    }, 1000);
}
document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        selectable: true,
        events: '/get-events',  // Load events from Flask route
        select: function(info) {
            const title = prompt('Enter project title:');
            if (title) {
                const newEvent = {
                    title: title,
                    start: info.startStr,
                    end: info.endStr
                };
                // Send the new event to the server
                fetch('/add-event', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(newEvent)
                })
                .then(response => response.json())
                .then(event => {
                    calendar.addEvent(event);  // Add to calendar view
                    alert('Event added successfully');
                })
                .catch(error => console.error('Error:', error));
            }
            calendar.unselect();
        }
    });

    calendar.render();
});
