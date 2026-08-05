document.addEventListener('DOMContentLoaded', () => {
  const matrix = document.querySelector('.jp-matrix');
  if (!matrix) return;

  const chars = ['O', 'W', 'o', 'w'];
  const particles = [];
  const initialCount = 400;

  // Function to create a particle object
  function createParticle(x, y, isSpawned = false) {
    const span = document.createElement('span');
    span.textContent = chars[Math.floor(Math.random() * chars.length)];
    
    // Random font size between 32px and 55px
    const size = Math.floor(Math.random() * 24) + 32;
    span.style.fontSize = `${size}px`;
    
    // Set initial position
    span.style.left = '0px';
    span.style.top = '0px';
    span.style.transform = `translate3d(${x}px, ${y}px, 0)`;

    // Randomize pulse animation duration and phase for each character
    const duration = (Math.random() * 3.5 + 2.5).toFixed(2); // 2.5s to 6.0s
    const delay = (Math.random() * -6).toFixed(2); // Starts mid-cycle immediately
    span.style.animation = `smooth-pulse ${duration}s ease-in-out infinite ${delay}s`;

    matrix.appendChild(span);

    // Random velocities (slow drifting speeds)
    // Spawned particles can have a slightly higher initial velocity for visual feedback
    const speedMultiplier = isSpawned ? 2.0 : 1.0;
    let vx = (Math.random() * 0.8 - 0.4) * speedMultiplier;
    let vy = (Math.random() * 0.8 - 0.4) * speedMultiplier;

    // Avoid zero velocity
    if (Math.abs(vx) < 0.1) vx = 0.15 * (Math.random() > 0.5 ? 1 : -1);
    if (Math.abs(vy) < 0.1) vy = 0.15 * (Math.random() > 0.5 ? 1 : -1);

    const particle = {
      element: span,
      x: x,
      y: y,
      vx: vx,
      vy: vy,
      size: size
    };

    particles.push(particle);
  }

  // Populate initial particles
  const docWidth = document.documentElement.scrollWidth || window.innerWidth;
  const docHeight = document.documentElement.scrollHeight || window.innerHeight;

  for (let i = 0; i < initialCount; i++) {
    const rx = Math.random() * docWidth;
    const ry = Math.random() * docHeight;
    createParticle(rx, ry);
  }

  // Animation Loop using requestAnimationFrame
  function updateAnimation() {
    // Re-evaluate boundaries in case of dynamically resizing page elements
    const currentWidth = document.documentElement.scrollWidth || window.innerWidth;
    const currentHeight = document.documentElement.scrollHeight || window.innerHeight;

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;

      // Wrap-around bounds checking
      const buffer = p.size + 10;
      if (p.x < -buffer) {
        p.x = currentWidth + buffer;
      } else if (p.x > currentWidth + buffer) {
        p.x = -buffer;
      }

      if (p.y < -buffer) {
        p.y = currentHeight + buffer;
      } else if (p.y > currentHeight + buffer) {
        p.y = -buffer;
      }

      // Update position with GPU-accelerated translate3d
      p.element.style.transform = `translate3d(${p.x}px, ${p.y}px, 0)`;
    }

    requestAnimationFrame(updateAnimation);
  }

  requestAnimationFrame(updateAnimation);

  // Click handler to spawn particles on background clicks
  document.addEventListener('click', (e) => {
    // Only spawn if click target is not an interactive button, link, inputs or dashboard cards
    const target = e.target;
    const isInteractive = target.closest('button, a, input, select, textarea, .card, header, .topbar, .auth-tabs');
    
    if (!isInteractive) {
      // Spawn 1 to 2 random-sized letters at the exact cursor coordinates
      createParticle(e.pageX, e.pageY, true);
    }
  });
});
