const animatedElements = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-zoom');

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('active');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.14, rootMargin: '0px 0px -40px 0px' });

animatedElements.forEach(el => observer.observe(el));

window.addEventListener('scroll', () => {
  const header = document.querySelector('header');
  header.style.boxShadow = window.scrollY > 30 ? '0 15px 45px rgba(0,0,0,.28)' : 'none';
});
