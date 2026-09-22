(() => {
  document.querySelectorAll('[data-ranker-lab]').forEach((lab) => {
    const field = (name) => lab.querySelector(`[data-field="${name}"]`);
    const output = (name) => lab.querySelector(`[data-output="${name}"]`);

    const update = () => {
      const venue = Number(field('venue').value);
      const category = Number(field('category').value);
      const confidence = Number(field('confidence').value);
      const weekendDelta = Number(field('weekend-delta').value);
      const explicitChoice = Number(field('explicit').value);
      const weekend = field('weekend').checked;
      const baseline = Number(field('baseline').value);
      const aggregateNovelty = Number(field('aggregate-novelty').value);
      const familiar = field('familiar').checked;
      const sparse = confidence < 0.5;

      const inferred = 0.6 * venue + 0.4 * category;
      const confidenceAdjusted = sparse
        ? 0.5
        : confidence * inferred + (1 - confidence) * 0.5;
      const contextAdjustment = weekend && !sparse ? confidence * weekendDelta : 0;
      const applied = Math.min(1, Math.max(0,
        0.7 * explicitChoice + 0.3 * confidenceAdjusted + contextAdjustment,
      ));
      const categoryDiscovery = familiar ? 0 : 1;
      const novelty = 0.65 * aggregateNovelty + 0.35 * categoryDiscovery;
      const noveltyWeight = applied ** 1.5;
      const finalScore = (1 - noveltyWeight) * baseline + noveltyWeight * novelty;

      output('inferred').textContent = inferred.toFixed(4);
      output('confidence-adjusted').textContent = confidenceAdjusted.toFixed(4);
      output('context-adjustment').textContent = contextAdjustment.toFixed(4);
      output('applied').textContent = applied.toFixed(4);
      output('category-discovery').textContent = categoryDiscovery.toFixed(0);
      output('novelty').textContent = novelty.toFixed(4);
      output('novelty-weight').textContent = noveltyWeight.toFixed(4);
      output('final').textContent = finalScore.toFixed(4);
      output('fallback').textContent = sparse ? 'Yes — neutral inferred signal' : 'No';
      lab.querySelectorAll('[data-current]').forEach((node) => {
        const source = field(node.dataset.current);
        node.textContent = source.type === 'checkbox'
          ? (source.checked ? 'on' : 'off')
          : Number(source.value).toFixed(2);
      });
    };

    lab.querySelectorAll('input, select').forEach((control) => {
      control.addEventListener('input', update);
      control.addEventListener('change', update);
    });
    update();
  });
})();
