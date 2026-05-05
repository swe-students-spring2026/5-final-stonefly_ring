document.addEventListener('DOMContentLoaded', () => {
    countUpBalance();
    initRipple();
    initAutoSplit();
    initFormLoadingState();
    initCharCounter();
    initScrollHeader();
    maybeFireConfetti();
});

// ── 1. Count-up animation on balance ────────────────────────────────
function countUpBalance() {
    const el = document.querySelector('.balance-amount');
    if (!el) return;

    const match = el.textContent.trim().replace(/,/g, '').match(/([\d.]+)/);
    if (!match) return;

    const target   = parseFloat(match[1]);
    const duration = 950;
    const start    = performance.now();

    el.textContent = '$0.00';

    function step(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased    = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        el.textContent = '$' + (target * eased).toFixed(2);
        if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
}

// ── 2. Ripple on buttons ─────────────────────────────────────────────
function initRipple() {
    document.querySelectorAll('.btn-primary, .btn-inline, .header-action').forEach(btn => {
        btn.addEventListener('click', function (e) {
            const rect = this.getBoundingClientRect();
            const x    = e.clientX - rect.left;
            const y    = e.clientY - rect.top;

            const dot = document.createElement('span');
            dot.className = 'ripple-dot';
            dot.style.left = x + 'px';
            dot.style.top  = y + 'px';

            this.appendChild(dot);
            dot.addEventListener('animationend', () => dot.remove());
        });
    });
}

// ── 3. Auto-split on add-expense form ───────────────────────────────
function initAutoSplit() {
    const totalInput = document.querySelector('input[name="total_amount"]');
    const owedInput  = document.querySelector('input[name="amount_owed"]');
    if (!totalInput || !owedInput) return;

    // Show a hint badge next to the owed label
    const label = owedInput.closest('.form-group')?.querySelector('.form-label');
    if (label && !label.querySelector('.split-hint')) {
        const hint = document.createElement('span');
        hint.className = 'split-hint';
        hint.textContent = 'auto 50/50';
        label.appendChild(hint);
    }

    let userEditedOwed = false;

    owedInput.addEventListener('input', () => { userEditedOwed = true; });

    totalInput.addEventListener('input', () => {
        const total = parseFloat(totalInput.value);
        if (!isNaN(total) && total >= 0 && !userEditedOwed) {
            owedInput.value = (total / 2).toFixed(2);
            pulseInput(owedInput);
        }
        validateSplit(totalInput, owedInput);
    });

    owedInput.addEventListener('input', () => {
        validateSplit(totalInput, owedInput);
    });
}

function validateSplit(totalInput, owedInput) {
    const total = parseFloat(totalInput.value);
    const owed  = parseFloat(owedInput.value);
    let warning = owedInput.parentElement.querySelector('.split-warning');

    if (!isNaN(total) && !isNaN(owed) && owed > total) {
        if (!warning) {
            warning = document.createElement('span');
            warning.className = 'split-warning';
            owedInput.parentElement.appendChild(warning);
        }
        warning.textContent = '⚠️ Can\'t owe more than the total';
        owedInput.style.borderColor = 'var(--negative)';
    } else {
        warning?.remove();
        owedInput.style.borderColor = '';
    }
}

function pulseInput(el) {
    el.style.transition = 'background 0.15s';
    el.style.background = 'rgba(99,102,241,0.08)';
    setTimeout(() => { el.style.background = ''; }, 300);
}

// ── 4. Form loading state ────────────────────────────────────────────
function initFormLoadingState() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function () {
            const btn = this.querySelector('.btn-primary');
            if (!btn || btn.disabled) return;

            const original = btn.innerHTML;
            btn.innerHTML  = '<span class="spinner"></span> Loading…';
            btn.disabled   = true;

            // Safety reset in case navigation fails
            setTimeout(() => {
                btn.innerHTML = original;
                btn.disabled  = false;
            }, 5000);
        });
    });
}

// ── 5. Confetti burst when you're owed money ─────────────────────────
function maybeFireConfetti() {
    if (!document.querySelector('.balance-amount.positive')) return;

    const key = 'confetti_' + window.location.pathname;
    if (sessionStorage.getItem(key)) return;
    sessionStorage.setItem(key, '1');

    const colors = ['#6366f1','#8b5cf6','#ec4899','#f59e0b','#10b981','#06b6d4','#f97316'];

    setTimeout(() => {
        for (let i = 0; i < 80; i++) {
            const p      = document.createElement('div');
            const size   = Math.random() * 9 + 4;
            const circle = Math.random() > 0.45;
            const color  = colors[Math.floor(Math.random() * colors.length)];
            const dur    = (Math.random() * 2.2 + 1.3).toFixed(2);
            const delay  = (Math.random() * 0.9).toFixed(2);
            const left   = (Math.random() * 100).toFixed(1);
            const spin   = Math.random() > 0.5 ? 'confetti-spin' : '';

            p.style.cssText = [
                `position:fixed`,
                `width:${size}px`,
                `height:${size}px`,
                `background:${color}`,
                `border-radius:${circle ? '50%' : '2px'}`,
                `left:${left}vw`,
                `top:-14px`,
                `z-index:9999`,
                `pointer-events:none`,
                `animation:confetti-fall ${dur}s ease-in forwards ${spin}`,
                `animation-delay:${delay}s`,
            ].join(';');

            document.body.appendChild(p);
            p.addEventListener('animationend', () => p.remove());
        }
    }, 800);
}

// ── 6. Description character counter ─────────────────────────────────
function initCharCounter() {
    const desc = document.querySelector('input[name="description"]');
    if (!desc) return;

    const MAX = 60;
    desc.setAttribute('maxlength', MAX);

    const counter = document.createElement('span');
    counter.className = 'char-counter';
    counter.textContent = `0 / ${MAX}`;
    desc.parentElement.appendChild(counter);

    desc.addEventListener('input', () => {
        const len = desc.value.length;
        counter.textContent = `${len} / ${MAX}`;
        counter.classList.toggle('char-counter--warn', len > MAX * 0.85);
    });
}

// ── 7. Sticky header elevation on scroll ─────────────────────────────
function initScrollHeader() {
    const header = document.querySelector('.page-header');
    if (!header) return;

    const content = document.querySelector('.content');
    if (!content) return;

    content.addEventListener('scroll', () => {
        header.classList.toggle('page-header--elevated', content.scrollTop > 8);
    }, { passive: true });
}
