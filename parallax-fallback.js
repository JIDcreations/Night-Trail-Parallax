// Fallback for browsers without CSS scroll-driven animations.
// It recreates what parallax.css does: layers slide by speed, scenes crossfade,
// the reel moves sideways. Browsers that support animation-timeline never run this.

if (!CSS.supports('animation-timeline: view()')) {
  const still = matchMedia('(prefers-reduced-motion: reduce)');
  const clamp = (v) => Math.min(1, Math.max(0, v));

  const scenes = [...document.querySelectorAll('.scene')].map((el) => ({
    el,
    stage: el.querySelector('.stage'),
    layers: [...el.querySelectorAll('.layer')],
  }));
  const reel = document.querySelector('.reel');
  const track = reel.querySelector('.reel__track');
  const reelLayer = reel.querySelector('.layer');
  const reelImages = [...reel.querySelectorAll('.reel__frame img')];
  const route = document.querySelector('.route__progress');

  // without a scroll timeline these CSS animations would just play once and stop, so switch them off
  for (const el of document.querySelectorAll('.stage, .layer, .reel__track, .reel__frame img, .route__progress')) {
    el.style.animation = 'none';
  }

  // the layer is exactly (speed × travel) wider than its stage: that's how far it moves
  const slide = (layer, progress) => {
    const distance = layer.offsetWidth - layer.parentElement.offsetWidth;
    layer.style.translate = `${-distance * progress}px 0`;
  };

  function update() {
    const vh = innerHeight;

    for (const { el, stage, layers } of scenes) {
      const box = el.getBoundingClientRect();
      const cover = clamp((vh - box.top) / (box.height + vh));    // animation-range: cover
      const entry = clamp((vh - box.top) / vh);
      const exit = clamp(box.bottom / vh);
      const opacity = Math.min(entry, exit);
      stage.style.opacity = opacity;
      stage.style.visibility = opacity > 0 ? 'visible' : 'hidden';
      if (!still.matches) layers.forEach((layer) => slide(layer, cover));
    }

    const box = reel.getBoundingClientRect();
    const contain = clamp(-box.top / (box.height - vh));            // animation-range: contain
    track.style.translate = `${-(track.offsetWidth - innerWidth) * contain}px 0`;
    if (!still.matches) {
      slide(reelLayer, contain);
      reelImages.forEach((img) => (img.style.translate = `${-8 + 16 * contain}% 0`));
    }

    route.style.scale = `${clamp(scrollY / (document.documentElement.scrollHeight - vh))} 1`;
  }

  let queued = false;
  const request = () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => { queued = false; update(); });
  };

  addEventListener('scroll', request, { passive: true });
  addEventListener('resize', request);
  update();
}
