// Earthquake Alarm System
(function() {
    let knownEarthquakeIds = new Set();
    let audioContext = null;
    let isAudioInitialized = false;
    
    // Initialize audio context on first user interaction
    function initAudio() {
        if (!isAudioInitialized) {
            try {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                isAudioInitialized = true;
                console.log('🔊 Audio system initialized');
            } catch (e) {
                console.error('Failed to initialize audio:', e);
            }
        }
    }
    
    // Play CRITICAL alarm - very loud and aggressive for magnitude 7+
    function playCriticalAlarm(times = 10) {
        if (!audioContext) {
            initAudio();
        }
        
        if (!audioContext) {
            console.error('Audio context not available');
            return;
        }
        
        let playCount = 0;
        
        function playUrgentSiren() {
            if (playCount >= times) return;
            
            // Create THREE oscillators for a much louder, more aggressive sound
            const osc1 = audioContext.createOscillator();
            const osc2 = audioContext.createOscillator();
            const osc3 = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            osc1.connect(gainNode);
            osc2.connect(gainNode);
            osc3.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            // Aggressive siren effect - rising pitch
            const startFreq = 400;
            const endFreq = 1200;
            const duration = 0.8;
            
            // Three oscillators at different frequencies for maximum loudness
            osc1.frequency.setValueAtTime(startFreq, audioContext.currentTime);
            osc1.frequency.exponentialRampToValueAtTime(endFreq, audioContext.currentTime + duration);
            
            osc2.frequency.setValueAtTime(startFreq * 1.5, audioContext.currentTime);
            osc2.frequency.exponentialRampToValueAtTime(endFreq * 1.5, audioContext.currentTime + duration);
            
            osc3.frequency.setValueAtTime(startFreq * 2, audioContext.currentTime);
            osc3.frequency.exponentialRampToValueAtTime(endFreq * 2, audioContext.currentTime + duration);
            
            // Use square wave for harsher, more attention-grabbing sound
            osc1.type = 'square';
            osc2.type = 'sawtooth';
            osc3.type = 'square';
            
            // MAXIMUM VOLUME - 0.8 (very loud!)
            gainNode.gain.setValueAtTime(0.8, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
            
            osc1.start(audioContext.currentTime);
            osc2.start(audioContext.currentTime);
            osc3.start(audioContext.currentTime);
            
            osc1.stop(audioContext.currentTime + duration);
            osc2.stop(audioContext.currentTime + duration);
            osc3.stop(audioContext.currentTime + duration);
            
            playCount++;
            
            if (playCount < times) {
                // Shorter gap between sirens for urgency
                setTimeout(playUrgentSiren, 400);
            }
        }
        
        playUrgentSiren();
    }
    
    // Play MAJOR alarm sound (for magnitude 6.0+) - loud and urgent
    function playMajorAlarm(times = 6) {
        if (!audioContext) {
            initAudio();
        }
        
        if (!audioContext) {
            console.error('Audio context not available');
            return;
        }
        
        let playCount = 0;
        
        function playUrgentBeep() {
            if (playCount >= times) return;
            
            // Use TWO oscillators for louder, more urgent sound
            const osc1 = audioContext.createOscillator();
            const osc2 = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            osc1.connect(gainNode);
            osc2.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            // Dual-tone alarm (alternating pattern)
            const freq1 = playCount % 2 === 0 ? 900 : 700;
            const freq2 = freq1 * 1.5;
            
            osc1.frequency.value = freq1;
            osc2.frequency.value = freq2;
            
            // Mix of square and sawtooth for urgency
            osc1.type = 'square';
            osc2.type = 'sawtooth';
            
            // Louder volume - 0.6 (was 0.4)
            gainNode.gain.setValueAtTime(0.6, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.6);
            
            osc1.start(audioContext.currentTime);
            osc2.start(audioContext.currentTime);
            
            osc1.stop(audioContext.currentTime + 0.6);
            osc2.stop(audioContext.currentTime + 0.6);
            
            playCount++;
            
            if (playCount < times) {
                setTimeout(playUrgentBeep, 500); // Faster - 500ms instead of 600ms
            }
        }
        
        playUrgentBeep();
    }
    
    // Play moderate alarm sound (for magnitude 5.0-5.9)
    function playModerateAlarm(times = 1) {
        if (!audioContext) {
            initAudio();
        }
        
        if (!audioContext) {
            console.error('Audio context not available');
            return;
        }
        
        let playCount = 0;
        
        function playBeep() {
            if (playCount >= times) return;
            
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            // Single tone alarm
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.4, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
            
            playCount++;
            
            if (playCount < times) {
                setTimeout(playBeep, 600);
            }
        }
        
        playBeep();
    }
    
    // Play iPhone-like text message sound (tri-tone)
    function playTextSound() {
        if (!audioContext) {
            initAudio();
        }
        
        if (!audioContext) {
            console.error('Audio context not available');
            return;
        }
        
        // iPhone tri-tone: three quick notes
        const notes = [1000, 800, 600]; // Frequencies in Hz
        const noteDuration = 0.15; // seconds
        const noteGap = 0.05; // seconds between notes
        
        notes.forEach((freq, index) => {
            const startTime = audioContext.currentTime + (index * (noteDuration + noteGap));
            
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = freq;
            oscillator.type = 'sine';
            
            // Envelope: quick attack, sustain, quick decay
            gainNode.gain.setValueAtTime(0, startTime);
            gainNode.gain.linearRampToValueAtTime(0.2, startTime + 0.02);
            gainNode.gain.setValueAtTime(0.2, startTime + noteDuration - 0.02);
            gainNode.gain.linearRampToValueAtTime(0, startTime + noteDuration);
            
            oscillator.start(startTime);
            oscillator.stop(startTime + noteDuration);
        });
    }
    
    // Show toast notification for minor earthquakes
    function showToast(magnitude, location) {
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
        
        toast.innerHTML = `
            <div class="toast-header">
                <span>📱</span>
                <span>Minor Earthquake Detected</span>
            </div>
            <div class="toast-body">
                <div><span class="toast-magnitude">Magnitude ${magnitude}</span></div>
                <div class="toast-location">${location}</div>
                <div class="toast-time">${timeString}</div>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            toast.classList.add('fade-out');
            // Remove from DOM after animation completes
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 5000);
    }
    
    // Check for new earthquakes and trigger alarm
    function checkForNewEarthquakes() {
        // Get the most recent earthquake from PHIVOLCS panel
        const phivolcsPanel = document.getElementById('phivolcs-panel');
        if (!phivolcsPanel) return;
        
        const earthquakes = phivolcsPanel.querySelectorAll('[data-eq-id]');
        if (earthquakes.length === 0) return;
        
        const latestEq = earthquakes[0];
        const eqId = latestEq.getAttribute('data-eq-id');
        const magnitude = parseFloat(latestEq.getAttribute('data-magnitude'));
        const location = latestEq.getAttribute('data-location').toLowerCase();
        
        // Check if this is a new earthquake
        if (!knownEarthquakeIds.has(eqId)) {
            knownEarthquakeIds.add(eqId);
            
            console.log(`🔊 New earthquake detected: M${magnitude} at ${location}`);
            
            // Special case: Manay with magnitude 7.0+ (critical local threat)
            if (magnitude >= 7.0 && location.includes('manay')) {
                console.log('🚨🚨🚨 CRITICAL: Manay 7.0+ - MAXIMUM ALERT SIREN!');
                playCriticalAlarm(10);
                showNotification('🚨 CRITICAL EARTHQUAKE', `Magnitude ${magnitude} in Manay! Take immediate action!`);
            } else if (magnitude >= 7.0) {
                console.log('🚨 Major 7.0+ earthquake - Critical alarm!');
                playCriticalAlarm(8);
                showNotification('🚨 MAJOR 7.0+ EARTHQUAKE', `Magnitude ${magnitude} detected!`);
            } else if (magnitude >= 6.0) {
                console.log('⚠️ Major earthquake (6.0+) - Loud alarm playing 6 times');
                playMajorAlarm(6);
                showNotification('⚠️ MAJOR EARTHQUAKE', `Magnitude ${magnitude} detected!`);
            } else if (magnitude >= 5.0) {
                console.log('⚠️ Moderate earthquake (5.0+) - Alarm playing once');
                playModerateAlarm(1);
                showNotification('⚠️ EARTHQUAKE ALERT', `Magnitude ${magnitude} detected`);
            } else {
                // Below 5.0 - no sound, show toast notification only
                console.log('📱 Minor earthquake (below 5.0) - Toast notification only');
                showToast(magnitude, location);
            }
        }
    }
    
    // Show browser notification
    function showNotification(title, message) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/static/favicon.ico',
                requireInteraction: true
            });
        }
    }
    
    // Request notification permission
    function requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize audio on first click
        document.addEventListener('click', initAudio, { once: true });
        
        // Request notification permission
        requestNotificationPermission();
        
        // Check for new earthquakes every 5 seconds
        setInterval(checkForNewEarthquakes, 5000);
        
        console.log('🔔 Earthquake alarm system initialized');
    });
})();
