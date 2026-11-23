(() => {
  const toggle = document.querySelector('.menu-toggle');
  const menu = document.querySelector('#mobile-nav');
  if (toggle && menu) {
    const close = () => {
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Open menu');
      menu.hidden = true;
    };
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      menu.hidden = !open;
    });
    menu.addEventListener('click', event => {
      if (event.target.closest('a')) close();
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape') close();
    });
    matchMedia('(min-width: 801px)').addEventListener('change', close);
  }

  const hero = document.querySelector('.hero');
  const canvas = hero?.querySelector('.starfield');
  const context = canvas?.getContext('2d', { alpha: true });
  if (!hero || !canvas || !context) return;

  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const pointer = { x: 0, y: 0, targetX: 0, targetY: 0, active: false };
  let width = 0;
  let height = 0;
  let stars = [];
  let visible = true;
  let frame = 0;
  let lastDraw = 0;

  const createStars = () => {
    let seed = 71453;
    const random = () => {
      seed = (seed * 16807) % 2147483647;
      return (seed - 1) / 2147483646;
    };
    const count = Math.min(230, Math.max(95, Math.round(width * height / 6100)));
    stars = Array.from({ length: count }, () => ({
      x: random(),
      y: random() * .82,
      size: .35 + random() * 1.5,
      depth: .3 + random() * .7,
      phase: random() * Math.PI * 2,
      speed: .45 + random() * 1.25,
      tint: random() > .84 ? '181,226,210' : '226,237,243'
    }));
  };

  const resize = () => {
    const bounds = hero.getBoundingClientRect();
    width = bounds.width;
    height = bounds.height;
    const ratio = Math.min(devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    createStars();
    if (motion.matches) render(0);
  };

  const render = time => {
    context.clearRect(0, 0, width, height);
    pointer.x += (pointer.targetX - pointer.x) * .045;
    pointer.y += (pointer.targetY - pointer.y) * .045;
    const nearby = [];

    for (const star of stars) {
      const x = star.x * width + pointer.x * star.depth * 17;
      const y = star.y * height + pointer.y * star.depth * 11;
      const shimmer = motion.matches ? .72 : .62 + .38 * Math.sin(time * .0007 * star.speed + star.phase);
      const alpha = (.28 + shimmer * .58) * star.depth;
      context.fillStyle = 'rgba(' + star.tint + ',' + alpha + ')';
      context.beginPath();
      context.arc(x, y, star.size, 0, Math.PI * 2);
      context.fill();
      if (star.size > 1.52) {
        context.fillStyle = 'rgba(211,239,226,' + alpha * .12 + ')';
        context.beginPath();
        context.arc(x, y, star.size * 4, 0, Math.PI * 2);
        context.fill();
      }
      if (pointer.active && !motion.matches) {
        const distance = Math.hypot(x - pointer.targetX, y - pointer.targetY);
        if (distance < 130) nearby.push({ x, y, distance });
      }
    }

    if (pointer.active && !motion.matches && pointer.targetX > width * .36) {
      nearby.sort((a, b) => a.distance - b.distance);
      context.lineWidth = 1;
      for (const star of nearby.slice(0, 4)) {
        context.strokeStyle = 'rgba(188,234,212,' + (1 - star.distance / 130) * .25 + ')';
        context.beginPath();
        context.moveTo(pointer.targetX, pointer.targetY);
        context.lineTo(star.x, star.y);
        context.stroke();
      }
      context.strokeStyle = 'rgba(198,236,217,.34)';
      context.beginPath();
      context.arc(pointer.targetX, pointer.targetY, 22, 0, Math.PI * 2);
      context.stroke();
      context.fillStyle = 'rgba(213,246,225,.72)';
      context.beginPath();
      context.arc(pointer.targetX, pointer.targetY, 2, 0, Math.PI * 2);
      context.fill();
    }
  };

  const tick = time => {
    if (!visible || document.hidden || motion.matches) {
      frame = 0;
      return;
    }
    if (time - lastDraw >= 30) {
      render(time);
      lastDraw = time;
    }
    frame = requestAnimationFrame(tick);
  };
  const start = () => {
    if (motion.matches) {
      if (frame) cancelAnimationFrame(frame);
      frame = 0;
      render(0);
    } else if (visible && !document.hidden && !frame) {
      frame = requestAnimationFrame(tick);
    }
  };

  hero.addEventListener('pointermove', event => {
    if (motion.matches || event.pointerType === 'touch') return;
    const bounds = hero.getBoundingClientRect();
    pointer.targetX = event.clientX - bounds.left;
    pointer.targetY = event.clientY - bounds.top;
    pointer.active = true;
  }, { passive: true });
  hero.addEventListener('pointerleave', () => { pointer.active = false; });
  document.addEventListener('visibilitychange', start);
  motion.addEventListener('change', start);
  window.addEventListener('resize', resize, { passive: true });
  new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting;
    start();
  }).observe(hero);
  resize();
  start();
})();
