// Exploded view: E (or the "Layers" button) toggles body.exploded.
// exploded.css then turns each scene's .rig in 3D and pulls its layers apart.

const explodeButton = document.querySelector('.hud__explode');

function addLabels() {
  for (const rig of document.querySelectorAll('.rig')) {
    for (const layer of rig.querySelectorAll('.layer')) {
      const style = getComputedStyle(layer);
      const name = [...layer.classList].find((c) => c.startsWith('layer--')).slice(7);
      const label = document.createElement('span');
      label.className = 'layer-label';
      label.textContent = `${name} · speed ${style.getPropertyValue('--speed').trim()}`;
      label.style.top = `${layer.offsetTop}px`;
      label.style.setProperty('--z', style.getPropertyValue('--z'));
      rig.append(label);
    }
  }
}

function toggleExploded() {
  if (!document.querySelector('.layer-label')) addLabels();
  const on = document.body.classList.toggle('exploded');
  explodeButton.setAttribute('aria-pressed', on);
  console.log(`[exploded] ${on ? 'on' : 'off'}`, document.body.className);
}

addEventListener('keydown', (e) => {
  if (e.key.toLowerCase() !== 'e' || e.metaKey || e.ctrlKey || e.altKey || e.repeat) return;
  if (e.target.closest('input, textarea, select, [contenteditable]')) return;  // typing, not toggling
  toggleExploded();
});

explodeButton.addEventListener('click', toggleExploded);
