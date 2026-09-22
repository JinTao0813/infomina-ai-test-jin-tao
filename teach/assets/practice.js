(() => {
  const practices = document.querySelectorAll('[data-practice]');
  practices.forEach((practice) => {
    const score = practice.querySelector('.score');
    const states = new Map();
    practice.querySelectorAll('.grade-row').forEach((row, index) => {
      row.querySelectorAll('button').forEach((button) => {
        button.addEventListener('click', () => {
          row.querySelectorAll('button').forEach((item) => item.setAttribute('aria-pressed', 'false'));
          button.setAttribute('aria-pressed', 'true');
          states.set(index, button.dataset.grade);
          const known = [...states.values()].filter((value) => value === 'known').length;
          const almost = [...states.values()].filter((value) => value === 'almost').length;
          const missed = [...states.values()].filter((value) => value === 'missed').length;
          score.textContent = `${states.size} graded · ${known} solid · ${almost} revisit · ${missed} missed`;
        });
      });
    });
  });
})();
