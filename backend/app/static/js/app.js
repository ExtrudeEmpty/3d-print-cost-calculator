/* ═══════════════════════════════════════════════════════
   3D-Druck Kostenrechner — app.js
   Vanilla JS: API helpers, modals, toasts, utilities
   ═══════════════════════════════════════════════════════ */

// ── API Helpers ─────────────────────────────────────

async function apiGet(url) {
    const res = await fetch(url);
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        console.error(`API Error [GET] ${url}:`, err.detail || res.statusText);
        throw new Error(err.detail || t('server_error'));
    }
    return res.json();
}

async function apiPost(url, data) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || t('server_error'));
    }
    return res.json();
}

async function apiPut(url, data) {
    const res = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || t('server_error'));
    }
    return res.json();
}

async function apiDelete(url) {
    const res = await fetch(url, { method: 'DELETE' });
    if (!res.ok && res.status !== 204) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || t('server_error'));
    }
    return true;
}


// ── Formatting ──────────────────────────────────────

function setAccent(accent) {
    if (!accent) accent = localStorage.getItem('app-accent') || 'green';
    document.documentElement.setAttribute('data-accent', accent);
    localStorage.setItem('app-accent', accent);
    
    // Update active state in UI if on settings page
    document.querySelectorAll('.accent-dot').forEach(dot => {
        dot.classList.toggle('active', dot.dataset.accent === accent);
    });
}

function formatCurrency(value) {
    if (value === null || value === undefined) return '—';
    
    // Get settings from localStorage (saved during loadPreferences)
    const symbol = localStorage.getItem('app-currency-symbol') || '€';
    const position = localStorage.getItem('app-currency-position') || 'end_with_space';
    const numberLocale = localStorage.getItem('app-number-locale') || 'de-DE';

    // Format the number part first
    const formattedNumber = new Intl.NumberFormat(numberLocale, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(value);

    // Apply currency symbol and position
    switch (position) {
        case 'start':
            return `${symbol}${formattedNumber}`;
        case 'start_with_space':
            return `${symbol} ${formattedNumber}`;
        case 'end':
            return `${formattedNumber}${symbol}`;
        case 'end_with_space':
        default:
            return `${formattedNumber} ${symbol}`;
    }
}

function formatNumber(value, decimals = 2) {
    if (value === null || value === undefined) return '—';
    const numberLocale = localStorage.getItem('app-number-locale') || 'de-DE';
    
    return new Intl.NumberFormat(numberLocale, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
    }).format(value);
}


function formatDate(dateStr) {
    if (!dateStr) return '—';
    const dateFormat = localStorage.getItem('app-date-format') || 'DD.MM.YYYY';
    
    // dateStr is usually YYYY-MM-DD from the backend
    const parts = dateStr.split('T')[0].split('-');
    if (parts.length !== 3) return dateStr;
    
    const [year, month, day] = parts;

    switch (dateFormat) {
        case 'MM/DD/YYYY':
            return `${month}/${day}/${year}`;
        case 'YYYY-MM-DD':
            return `${year}-${month}-${day}`;
        case 'DD.MM.YYYY':
        default:
            return `${day}.${month}.${year}`;
    }
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}


// ── Toast Notifications ─────────────────────────────

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const iconMap = {
        'success': 'check',
        'error': 'x',
        'info': 'info-circle'
    };
    const iconName = iconMap[type] || 'check';
    toast.innerHTML = `<span><svg class="icon" width="24" height="24" viewBox="0 0 24 24"><use href="/static/icons/tabler-sprite.svg#tabler-${iconName}"></use></svg></span> ${escapeHtml(message)}`;
    container.appendChild(toast);

    setTimeout(() => {
        if (toast.parentNode) toast.remove();
    }, 3000);
}

function showInfo(event, key) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    showToast(t(key), 'info');
}


// ── Modal ───────────────────────────────────────────

function openModal() {
    document.getElementById('modal-overlay').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
    document.body.style.overflow = '';
}

function openConfirmModal(title, message, onConfirm) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = `
        <div class="confirm-dialog">
            <p>${escapeHtml(message)}</p>
        </div>
    `;
    document.getElementById('modal-footer').innerHTML = `
        <button class="btn btn-secondary" onclick="closeModal()">
            <svg class="icon" width="24" height="24" viewBox="0 0 24 24"><use href="/static/icons/tabler-sprite.svg#tabler-x"></use></svg>
            ${t('cancel')}
        </button>
        <button class="btn btn-danger" id="confirm-btn">
            <svg class="icon" width="24" height="24" viewBox="0 0 24 24"><use href="/static/icons/tabler-sprite.svg#tabler-trash"></use></svg>
            ${t('delete')}
        </button>
    `;

    document.getElementById('confirm-btn').addEventListener('click', async () => {
        try {
            await onConfirm();
        } catch (err) {
            showToast(t('error') + ': ' + err.message, 'error');
        }
        closeModal();
    });

    openModal();
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
    if (e.target.id === 'modal-overlay') {
        closeModal();
    }
});

// Close modal on Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});


// ── Mobile Sidebar & Submenu Toggle ─────────────────

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

function toggleMobileSubmenu(event) {
    if (event) event.stopPropagation();
    const overlay = document.getElementById('mobile-submenu-overlay');
    overlay.classList.toggle('active');
    
    if (overlay.classList.contains('active')) {
        document.body.style.overflow = 'hidden';
    } else {
        document.body.style.overflow = '';
    }
}

// Close sidebar or submenu on mobile when clicking outside
document.addEventListener('click', (e) => {
    // Sidebar
    const sidebar = document.getElementById('sidebar');
    const hamburger = document.querySelector('.hamburger');
    if (sidebar && sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) &&
        (hamburger && !hamburger.contains(e.target))) {
        sidebar.classList.remove('open');
    }
});

// ── Preferences (Translation & Theme) ───────────────

let translations = {};

function t(key) {
    return translations[key] || key;
}

async function loadPreferences() {
    try {
        const prefs = await apiGet('/api/settings/preferences');
        
        // Theme
        setTheme(prefs.theme);
        
        // Localization & Formatting
        localStorage.setItem('app-lang', prefs.language || 'en');
        localStorage.setItem('app-number-locale', prefs.number_format_locale || 'de-DE');
        localStorage.setItem('app-date-format', prefs.date_format || 'DD.MM.YYYY');
        localStorage.setItem('app-currency-symbol', prefs.currency_symbol || '€');
        localStorage.setItem('app-currency-position', prefs.currency_position || 'end_with_space');

        // Update UI if on settings page
        if (document.getElementById('lang-select')) {
            document.getElementById('lang-select').value = prefs.language;
            document.getElementById('number-locale-select').value = prefs.number_format_locale;
            document.getElementById('date-format-select').value = prefs.date_format;
            document.getElementById('currency-symbol-select').value = prefs.currency_symbol;
            document.getElementById('currency-pos-select').value = prefs.currency_position;
        }

        await loadTranslations(prefs.language || 'en');
        setAccent(prefs.accent);
        return prefs;
    } catch (err) {
        console.error('Failed to load preferences:', err);
        // Defaults
        setTheme('dark');
        setAccent();
        localStorage.setItem('app-lang', 'en');
        localStorage.setItem('app-number-locale', 'de-DE');
        localStorage.setItem('app-date-format', 'DD.MM.YYYY');
        localStorage.setItem('app-currency-symbol', '€');
        localStorage.setItem('app-currency-position', 'end_with_space');
        await loadTranslations('en');
        return { language: 'en', theme: 'dark' };
    }
}

/**
 * Parses a time string like '2d5h43m', '8:30', or '8.5' into float hours or int minutes.
 * Supports natural language units: d, day, days, h, hr, hrs, hour, hours, m, min, mins, minute, minutes
 */
function parseTimeInput(input, targetUnit = 'hours') {
    if (!input || input.toString().trim() === '') return 0;
    const originalInput = input.toString().trim();
    const str = originalInput.toLowerCase().replace(/\s/g, '');
    
    // 1. Flexible natural language format (e.g., 2d5h30m, 2days 5hrs 30mins)
    const flexibleRegex = /^(?:(\d+)(?:d|day|days))?(?:(\d+)(?:h|hr|hrs|hour|hours))?(?:(\d+)(?:m|min|mins|minute|minutes))?$/;
    const match = str.match(flexibleRegex);
    
    if (match && (match[1] || match[2] || match[3])) {
        const d = parseInt(match[1] || 0);
        const h = parseInt(match[2] || 0);
        const m = parseInt(match[3] || 0);
        const totalMinutes = (d * 24 * 60) + (h * 60) + m;
        return targetUnit === 'hours' ? totalMinutes / 60 : totalMinutes;
    }

    // 2. HH:MM or H:MM (Clock notation)
    const hhmmRegex = /^(\d+):([0-5]?\d)$/;
    const hhmmMatch = originalInput.match(hhmmRegex);
    if (hhmmMatch) {
        const h = parseInt(hhmmMatch[1]);
        const m = parseInt(hhmmMatch[2]);
        const totalMinutes = (h * 60) + m;
        return targetUnit === 'hours' ? totalMinutes / 60 : totalMinutes;
    }

    // 3. Decimal format (e.g., 8.5 or 8,5)
    const decimalStr = str.replace(',', '.');
    // Ensure it's a pure number without units before treating as decimal
    if (!isNaN(decimalStr) && decimalStr !== '' && !str.includes('d') && !str.includes('h') && !str.includes('m')) {
        const val = parseFloat(decimalStr);
        return targetUnit === 'hours' ? val : val * 60;
    }

    throw new Error('invalid_time_format');
}

/**
 * Formats a duration (float hours or int minutes) to "Xd Yh Zmin" or "Xh Ymin"
 * @param {boolean} showDays - If true, converts hours > 24 to days.
 */
function formatDuration(value, sourceUnit = 'hours', showDays = false) {
    if (value === null || value === undefined || isNaN(value)) return '0h 0min';
    
    let totalMinutes = Math.round(sourceUnit === 'hours' ? value * 60 : value);
    if (totalMinutes === 0) return '0h 0min';

    let d = 0;
    if (showDays) {
        d = Math.floor(totalMinutes / (24 * 60));
        totalMinutes %= (24 * 60);
    }
    
    const h = Math.floor(totalMinutes / 60);
    const m = totalMinutes % 60;

    let parts = [];
    if (showDays && d > 0) parts.push(`${d}d`);
    if (h > 0 || (showDays && d > 0)) parts.push(`${h}h`); 
    if (m > 0 || (parts.length === 0)) parts.push(`${m}min`);
    
    return parts.join(' ');
}

async function loadTranslations(langTag) {
    const langCode = langTag.split('-')[0]; // Extract 'de' from 'de-DE'
    try {
        const res = await fetch(`/static/locales/${langCode}.json?v=${new Date().getTime()}`);
        if (!res.ok) throw new Error('Locale not found');
        translations = await res.json();
        translatePage();
    } catch (err) {
        console.error('Failed to load translations:', err);
    }
}

function translatePage() {
    // Standard text content
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[key]) {
            el.textContent = translations[key];
        }
    });
    // Placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (translations[key]) {
            el.placeholder = translations[key];
        }
    });
    // Titles (tooltips)
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
        const key = el.getAttribute('data-i18n-title');
        if (translations[key]) {
            el.title = translations[key];
        }
    });

    // Generic Attribute Translations (e.g. data-i18n-attr="content:meta_description")
    document.querySelectorAll('[data-i18n-attr]').forEach(el => {
        const attrMapping = el.getAttribute('data-i18n-attr');
        if (attrMapping && attrMapping.includes(':')) {
            const [attr, key] = attrMapping.split(':');
            if (translations[key]) {
                el.setAttribute(attr, translations[key]);
            }
        }
    });

    // App Title
    if (translations['app_title_full']) {
        document.title = translations['app_title_full'];
    }
}

async function updateAllFormatting() {
    const data = {
        language: document.getElementById('lang-select').value,
        number_format_locale: document.getElementById('number-locale-select').value,
        date_format: document.getElementById('date-format-select').value,
        currency_symbol: document.getElementById('currency-symbol-select').value,
        currency_position: document.getElementById('currency-pos-select').value
    };

    try {
        await apiPut('/api/settings/formatting', data);
        
        // Update local storage
        localStorage.setItem('app-lang', data.language);
        localStorage.setItem('app-number-locale', data.number_format_locale);
        localStorage.setItem('app-date-format', data.date_format);
        localStorage.setItem('app-currency-symbol', data.currency_symbol);
        localStorage.setItem('app-currency-position', data.currency_position);

        // Reload to apply translation and formatting changes everywhere
        location.reload(); 
    } catch (err) {
        showToast(t('settings_update_failed') + ': ' + err.message, 'error');
    }
}

async function changeLanguage() {
    // Deprecated in favor of updateAllFormatting, but keeping for compatibility if called elsewhere
    updateAllFormatting();
}

async function toggleTheme() {
    const root = document.documentElement;
    const currentTheme = root.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    await setThemeDirect(newTheme);
}

async function setThemeDirect(newTheme) {
    try {
        await apiPut('/api/settings/theme', { theme: newTheme });
        localStorage.setItem('app-theme', newTheme);
        setTheme(newTheme);
    } catch (err) {
        showToast(t('theme_change_failed') + ': ' + err.message, 'error');
    }
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('app-theme', theme);
    document.body.setAttribute('data-theme', theme);
    
    // Desktop Sidebar Icon
    const icon = document.getElementById('theme-icon');
    if (icon) {
        const iconName = theme === 'dark' ? 'moon' : 'sun';
        icon.innerHTML = `<svg class="icon" width="24" height="24" viewBox="0 0 24 24"><use href="/static/icons/tabler-sprite.svg#tabler-${iconName}"></use></svg>`;
    }

    // Mobile Header Icon
    const mobileIcon = document.getElementById('theme-icon-mobile');
    if (mobileIcon) {
        const iconName = theme === 'dark' ? 'moon' : 'sun';
        mobileIcon.innerHTML = `<svg class="icon"><use href="/static/icons/tabler-sprite.svg#tabler-${iconName}"></use></svg>`;
    }

    // Settings Page Toggle Icon
    const settingsIcon = document.getElementById('theme-icon-settings');
    if (settingsIcon) {
        const iconName = theme === 'dark' ? 'moon' : 'sun';
        settingsIcon.innerHTML = `<svg class="icon" width="24" height="24" viewBox="0 0 24 24"><use href="/static/icons/tabler-sprite.svg#tabler-${iconName}"></use></svg>`;
    }
}

// Global initialization
window.appReady = (async () => {
    await loadPreferences();
})();

document.addEventListener('DOMContentLoaded', () => {
    // Re-apply theme to ensure all elements (including those in templates) are synchronized
    const savedTheme = localStorage.getItem('app-theme') || 'dark';
    setTheme(savedTheme);
});
