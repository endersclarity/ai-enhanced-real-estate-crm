// Debug script to force enter key to work
console.log('Debug script loading...');

function forceEnterKey() {
    const input = document.getElementById('chatInput');
    if (!input) {
        console.error('chatInput not found');
        return;
    }
    
    // Remove all existing listeners
    const newInput = input.cloneNode(true);
    input.parentNode.replaceChild(newInput, input);
    
    // Add fresh listener
    newInput.addEventListener('keydown', function(e) {
        console.log('Debug keydown:', e.key);
        if (e.key === 'Enter' || e.keyCode === 13) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Debug: Calling sendChatMessage');
            if (typeof sendChatMessage === 'function') {
                sendChatMessage();
            } else {
                console.error('sendChatMessage is not defined');
            }
        }
    });
    
    console.log('Debug: Fresh listener attached');
}

// Try immediately and after delays
setTimeout(forceEnterKey, 100);
setTimeout(forceEnterKey, 500);
setTimeout(forceEnterKey, 1000);
setTimeout(forceEnterKey, 2000);