function animatePoetry() {
    const poetry = document.querySelector('.poetry-text');
    if (poetry) {
        poetry.classList.add('fade-in');
    }
}

function formatStanzas() {
    const poetry = document.querySelector('.poetry-text');
    if (poetry) {
        const lines = poetry.innerHTML.split('<br>');
        if (lines.length > 0) {
            // Extract title (first line)
            const title = lines[0];
            const remainingLines = lines.slice(1).filter(line => line.trim());
            
            // Group remaining lines into stanzas of 4
            const stanzas = [];
            for (let i = 0; i < remainingLines.length; i += 4) {
                if (i + 4 <= remainingLines.length) {
                    stanzas.push(remainingLines.slice(i, i + 4));
                }
            }
            
            // Create HTML structure
            poetry.innerHTML = `
                <div class="poem-title">${title}</div>
                ${stanzas.map(stanza => `
                    <div class="stanza">
                        ${stanza.join('<br>')}
                    </div>
                `).join('')}
            `;
        }
    }
}

function copyToClipboard() {
    const poetryText = document.querySelector('.poetry-text').innerText;
    
    navigator.clipboard.writeText(poetryText).then(() => {
        // Show success message
        const notification = document.createElement('div');
        notification.className = 'copy-success';
        notification.textContent = '✓ Poem copied!';
        document.body.appendChild(notification);
        
        // Remove notification after 2 seconds
        setTimeout(() => {
            notification.remove();
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Theme management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('.theme-toggle svg');
    if (icon) {
        icon.innerHTML = theme === 'light' 
            ? '<path d="M20 15.31L23.31 12 20 8.69V4h-4.69L12 .69 8.69 4H4v4.69L.69 12 4 15.31V20h4.69L12 23.31 15.31 20H20v-4.69z"/>'
            : '<circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>';
    }
}

// Add theme toggle button to DOM
function addThemeToggle() {
    const button = document.createElement('button');
    button.className = 'theme-toggle';
    button.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"></svg>';
    button.onclick = toggleTheme;
    document.body.appendChild(button);
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    animatePoetry();
    formatStanzas();
    initTheme();
    addThemeToggle();
});
