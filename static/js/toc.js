// static/js/toc.js
(function () {
    if (window.__tocInitialized) return;
    window.__tocInitialized = true;

    function slugify(text) {
        return text.trim()
            .replace(/#$/, '') // remove any trailing '#'
            .toLowerCase()
            .normalize('NFKD') // attempt to normalize unicode
            .replace(/[\u0300-\u036f]/g, '') // remove diacritics
            .replace(/[^a-z0-9\u00a1-\uffff\s-]/g, '') // allow unicode, numbers, spaces and hyphens
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .replace(/^-+|-+$/g, '');
    }

    function buildToc(container, article) {
        // remove existing TOC if present
        const old = container.querySelector('#TableOfContents');
        if (old) old.remove();

        const headers = Array.from(article.querySelectorAll('h1,h2,h3,h4,h5,h6'))
            .filter(h => !h.closest('.book-tabs'));

        if (!headers.length) {
            // no headers -> no TOC
            return;
        }

        // ensure all headers have an id
        const used = new Set();
        headers.forEach(h => {
            if (!h.id) {
                let id = slugify(h.textContent || 'heading');
                let i = 1;
                while (used.has(id) || document.getElementById(id)) {
                    id = `${id}-${i++}`;
                }
                h.id = id;
                used.add(id);
            } else {
                used.add(h.id);
            }
        });

        const levels = headers.map(h => parseInt(h.tagName.slice(1), 10));
        const minLevel = Math.min(...levels);

        const nav = document.createElement('nav');
        nav.id = 'TableOfContents';
        const rootUl = document.createElement('ul');

        let stack = [rootUl];      // stack of current ULs (root = level 0)
        let prevNorm = 0;
        let lastLi = null;

        headers.forEach(h => {
            const level = parseInt(h.tagName.slice(1), 10);
            const norm = level - minLevel;

            if (norm > prevNorm) {
                // create nested ULs inside the last existing LI
                for (let i = prevNorm; i < norm; i++) {
                    const newUl = document.createElement('ul');
                    if (lastLi) {
                        lastLi.appendChild(newUl);
                    } else {
                        // fallback: if no lastLi exists, attach the ul to the root
                        stack[stack.length - 1].appendChild(document.createElement('li')).appendChild(newUl);
                    }
                    stack.push(newUl);
                }
            } else if (norm < prevNorm) {
                for (let i = prevNorm; i > norm; i--) stack.pop();
            }

            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = `#${h.id}`;
            a.textContent = (h.textContent || '').trim().replace(/#$/, '');
            li.appendChild(a);
            stack[stack.length - 1].appendChild(li);

            lastLi = li;
            prevNorm = norm;
        });

        nav.appendChild(rootUl);
        container.appendChild(nav);
    }

    // check if containers are present (handles different classes/themes)
    function findContainers() {
        const tocContainer =
            document.querySelector('.book-toc-content') ||
            document.querySelector('.toc') ||
            document.querySelector('.site-toc') ||
            document.querySelector('aside.book-toc') ||
            null;

        const article =
            document.querySelector('.markdown.book-article') ||
            document.querySelector('article') ||
            document.querySelector('.content') ||
            null;

        if (!tocContainer || !article) return null;
        return { tocContainer, article };
    }

    function initOnce() {
        const nodes = findContainers();
        if (!nodes) return false;
        try {
            buildToc(nodes.tocContainer, nodes.article);
        } catch (e) {
            console.error('TOC build failed:', e);
        }
        return true;
    }

    // If DOMContentLoaded isn't enough (theme injects things via JS), observe the DOM
    document.addEventListener('DOMContentLoaded', function () {
        if (initOnce()) return;

        const obs = new MutationObserver((mutations, observer) => {
            if (initOnce()) observer.disconnect();
        });
        obs.observe(document.documentElement, { childList: true, subtree: true });

        // safety timeout: after 8s stop observing so the observer isn't left running indefinitely
        setTimeout(() => obs.disconnect(), 8000);
    });
})();