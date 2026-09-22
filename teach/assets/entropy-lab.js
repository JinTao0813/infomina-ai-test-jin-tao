(() => {
  const log2 = (value) => Math.log(value) / Math.log(2);
  document.querySelectorAll('[data-entropy-lab]').forEach((lab) => {
    const inputs = [...lab.querySelectorAll('input[type="range"]')];
    const totalNode = lab.querySelector('[data-total]');
    const kNode = lab.querySelector('[data-k]');
    const hNode = lab.querySelector('[data-h]');
    const maxNode = lab.querySelector('[data-max]');
    const normNode = lab.querySelector('[data-norm]');
    const bars = [...lab.querySelectorAll('.prob-bar')];
    const values = [...lab.querySelectorAll('[data-count]')];

    const update = () => {
      const counts = inputs.map((input) => Number(input.value));
      const total = counts.reduce((sum, count) => sum + count, 0);
      const positive = counts.filter((count) => count > 0);
      const k = positive.length;
      const probabilities = counts.map((count) => total > 0 ? count / total : 0);
      const entropy = probabilities.reduce((sum, p) => p > 0 ? sum - p * log2(p) : sum, 0);
      const maximum = k > 1 ? log2(k) : 0;
      const normalized = maximum > 0 ? entropy / maximum : 0;

      values.forEach((node, index) => { node.textContent = counts[index]; });
      bars.forEach((bar, index) => {
        const pct = `${(probabilities[index] * 100).toFixed(1)}%`;
        bar.style.setProperty('--p', pct);
        bar.setAttribute('aria-label', `Location ${index + 1}: ${pct}`);
      });
      totalNode.textContent = total;
      kNode.textContent = k;
      hNode.textContent = entropy.toFixed(3);
      maxNode.textContent = maximum.toFixed(3);
      normNode.textContent = normalized.toFixed(3);
    };

    inputs.forEach((input) => input.addEventListener('input', update));
    update();
  });
})();
