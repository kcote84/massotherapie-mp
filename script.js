(() => {
  'use strict';

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const header = document.querySelector('[data-header]');
  const navToggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.site-nav');
  const navLabel = navToggle?.querySelector('.sr-only');

  const setMenuState = (open) => {
    if (!navToggle || !nav || !header) return;

    navToggle.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('is-open', open);
    header.classList.toggle('is-open', open);
    document.body.classList.toggle('menu-open', open);

    if (navLabel) {
      navLabel.textContent = open ? 'Fermer le menu' : 'Ouvrir le menu';
    }
  };

  navToggle?.addEventListener('click', () => {
    const isOpen = navToggle.getAttribute('aria-expanded') === 'true';
    setMenuState(!isOpen);
  });

  nav?.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => setMenuState(false));
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && navToggle?.getAttribute('aria-expanded') === 'true') {
      setMenuState(false);
      navToggle?.focus();
    }
  });

  const updateHeader = () => {
    header?.classList.toggle('is-scrolled', window.scrollY > 24);
  };

  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });

  const revealElements = document.querySelectorAll('[data-reveal]');

  if (reducedMotion.matches || !('IntersectionObserver' in window)) {
    revealElements.forEach((element) => element.classList.add('is-visible'));
  } else {
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, {
      threshold: 0.12,
      rootMargin: '0px 0px -7% 0px'
    });

    revealElements.forEach((element) => revealObserver.observe(element));
  }

  const parallaxElement = document.querySelector('[data-parallax]');
  let parallaxFrame = null;

  const updateParallax = () => {
    parallaxFrame = null;
    if (!parallaxElement || reducedMotion.matches || window.innerWidth < 900) return;

    const shift = Math.min(window.scrollY * 0.055, 34);
    parallaxElement.style.setProperty('--portrait-shift', `${shift}px`);
  };

  window.addEventListener('scroll', () => {
    if (parallaxFrame === null) {
      parallaxFrame = window.requestAnimationFrame(updateParallax);
    }
  }, { passive: true });

  reducedMotion.addEventListener?.('change', () => {
    if (reducedMotion.matches && parallaxElement) {
      parallaxElement.style.removeProperty('--portrait-shift');
    } else {
      updateParallax();
    }
  });

  document.querySelectorAll('video').forEach((video) => {
    video.addEventListener('play', () => {
      document.querySelectorAll('video').forEach((otherVideo) => {
        if (otherVideo !== video && !otherVideo.paused) otherVideo.pause();
      });
    });
  });

  document.querySelectorAll('[data-year]').forEach((element) => {
    element.textContent = String(new Date().getFullYear());
  });

  const intro = document.querySelector('.intro');
  if (intro) {
    const removeIntro = () => intro.remove();
    intro.addEventListener('animationend', (event) => {
      if (event.animationName === 'intro-away') removeIntro();
    });
    window.setTimeout(removeIntro, reducedMotion.matches ? 0 : 2800);
  }

  window.addEventListener('resize', () => {
    if (window.innerWidth >= 1080) setMenuState(false);
    updateParallax();
  });

  updateParallax();
})();
