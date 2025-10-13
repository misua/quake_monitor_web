// Theme Management - Day/Night Mode based on time
(function() {
    function updateTheme() {
        const now = new Date();
        const hour = now.getHours();
        const minute = now.getMinutes();
        const body = document.getElementById('app-body');
        
        // Night mode: 17:30 (5:30 PM) to 06:30 (6:30 AM)
        // Convert to minutes for more precise comparison
        const currentMinutes = hour * 60 + minute;
        const nightStart = 17 * 60 + 30; // 5:30 PM
        const nightEnd = 6 * 60 + 30;    // 6:30 AM
        
        if (currentMinutes >= nightStart || currentMinutes < nightEnd) {
            body.classList.add('night-mode');
            body.classList.remove('day-mode');
            console.log('🌙 Night mode activated');
        } else {
            body.classList.add('day-mode');
            body.classList.remove('night-mode');
            console.log('☀️ Day mode activated');
        }
    }
    
    // Update theme on load
    updateTheme();
    
    // Check every minute for theme changes
    setInterval(updateTheme, 60000);
    
    // Also update on visibility change (when user returns to tab)
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            updateTheme();
        }
    });
})();

// Add smooth scroll behavior
document.documentElement.style.scrollBehavior = 'smooth';

// Console log for debugging
console.log('🌍 Earthquake & Weather Monitor - Web Version');
console.log('Theme system initialized');
