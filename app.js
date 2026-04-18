document.addEventListener('DOMContentLoaded', () => {
    // Configuration
    marked.setOptions({
        breaks: true,
        gfm: true,
        headerIds: true,
        highlight: function(code, lang) {
            if (Prism.languages[lang]) {
                return Prism.highlight(code, Prism.languages[lang], lang);
            } else {
                return code;
            }
        }
    });

    // Elements
    const links = document.querySelectorAll('.nav-links a');
    const contentDiv = document.getElementById('content');
    const loader = document.getElementById('loader');
    const searchInput = document.querySelector('.search-bar input');
    const themeToggle = document.getElementById('theme-toggle');

    // Theme toggle
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.body.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.body.setAttribute('data-theme', newTheme);
        themeToggle.innerHTML = newTheme === 'light' 
            ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>'
            : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
    });

    // Load content function
    async function loadContent(filename) {
        loader.classList.remove('hidden');
        contentDiv.classList.add('hidden');
        contentDiv.innerHTML = '';

        try {
            // Append cache busting string to bypass browser cache
            const response = await fetch(`${filename}?t=${new Date().getTime()}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const markdown = await response.text();
            
            // Parse markdown and sanitize
            const rawHtml = marked.parse(markdown);
            const cleanHtml = DOMPurify.sanitize(rawHtml, { USE_PROFILES: { html: true } });
            
            contentDiv.innerHTML = cleanHtml;
            
            // Re-highlight since we inject HTML
            Prism.highlightAllUnder(contentDiv);
            
            loader.classList.add('hidden');
            contentDiv.classList.remove('hidden');
            
            // Scroll to top
            document.querySelector('.markdown-container').scrollTop = 0;
            
        } catch (error) {
            console.error('Error loading markdown:', error);
            loader.classList.add('hidden');
            contentDiv.classList.remove('hidden');
            contentDiv.innerHTML = `
                <div style="text-align: center; padding: 3rem;">
                    <h2>⚠️ Unable to Load Document</h2>
                    <p style="color: var(--text-muted); margin-top: 1rem;">
                        Could not fetch <code>${filename}</code>.<br><br>
                        Make sure you are running this through a local web server (e.g., <code>npx serve</code>, VS Code Live Server, or Python's <code>python -m http.server</code>). Fetching local files via <code>file://</code> protocol is restricted by browsers.
                    </p>
                </div>
            `;
        }
    }

    // Navigation logic
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Update active state
            links.forEach(l => l.classList.remove('active'));
            e.currentTarget.classList.add('active');
            
            // Load file
            const file = e.currentTarget.getAttribute('data-file');
            loadContent(file);
        });
    });

    // Initial load
    const defaultFile = document.querySelector('.nav-links a.active').getAttribute('data-file');
    loadContent(defaultFile);

    // Search functionality (simple client-side highlight)
    searchInput.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        
        if (term.length > 2) {
            const elements = contentDiv.querySelectorAll('h1, h2, h3, h4, p, li');
            let found = false;
            
            elements.forEach(el => {
                const text = el.innerText.toLowerCase();
                if (text.includes(term)) {
                    el.style.backgroundColor = 'rgba(79, 70, 229, 0.2)';
                    el.style.borderRadius = '4px';
                    if (!found) {
                        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        found = true;
                    }
                } else {
                    el.style.backgroundColor = 'transparent';
                }
            });
        } else {
            const elements = contentDiv.querySelectorAll('h1, h2, h3, h4, p, li');
            elements.forEach(el => el.style.backgroundColor = 'transparent');
        }
    });
});
