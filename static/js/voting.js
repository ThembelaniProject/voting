(() => {
  const KEY = 'dj-battle-phase1-week-01';
  const seed = { dj1: 1250, dj2: 750 };
  const $ = id => document.getElementById(id);
  const freshState = () => ({ votes: {...seed}, votedFor: null, deadline: Date.now() + 7 * 24 * 60 * 60 * 1000 });
  const readState = () => {
    try {
      const saved = JSON.parse(localStorage.getItem(KEY));
      return saved && saved.votes && saved.deadline ? saved : freshState();
    } catch { return freshState(); }
  };
  let state = readState();
  const save = () => localStorage.setItem(KEY, JSON.stringify(state));
  const fmt = n => Number(n).toLocaleString('en-ZA');

  function render() {
    const total = state.votes.dj1 + state.votes.dj2;
    const p1 = total ? state.votes.dj1 / total * 100 : 0;
    const p2 = 100 - p1;
    $('dj1-votes').textContent = fmt(state.votes.dj1);
    $('dj2-votes').textContent = fmt(state.votes.dj2);
    $('dj1-percent').textContent = `${p1.toFixed(1)}%`;
    $('dj2-percent').textContent = `${p2.toFixed(1)}%`;
    $('dj1-bar').style.width = `${p1}%`;
    $('dj2-bar').style.width = `${p2}%`;
    $('total-votes').textContent = fmt(total);
    $('leader-one').textContent = fmt(state.votes.dj1);
    $('leader-two').textContent = fmt(state.votes.dj2);
    document.querySelectorAll('[data-vote]').forEach(btn => {
      const ended = Date.now() >= state.deadline;
      btn.disabled = Boolean(state.votedFor) || ended;
      if (state.votedFor) btn.textContent = state.votedFor === btn.dataset.vote ? 'YOUR VOTE IS CAST ✓' : 'VOTE ALREADY CAST';
      else if (ended) btn.textContent = 'VOTING HAS CLOSED';
    });
    if (state.votedFor) {
      $('vote-message').textContent = 'Thanks for supporting your DJ. This browser has used its vote for Week 01.';
      $('vote-confirm').hidden = false;
      $('vote-confirm').textContent = `Your vote for ${state.votedFor === 'dj1' ? 'DJ THUKZIN' : 'DJ MAPHO'} has been recorded in this browser.`;
    }
  }

  document.querySelectorAll('[data-vote]').forEach(btn => btn.addEventListener('click', () => {
    if (state.votedFor || Date.now() >= state.deadline) return;
    state.votes[btn.dataset.vote] += 1;
    state.votedFor = btn.dataset.vote;
    save();
    render();
  }));

  $('reset-demo').addEventListener('click', () => {
    localStorage.removeItem(KEY);
    state = freshState();
    $('vote-confirm').hidden = true;
    $('vote-message').textContent = 'Pick ONE DJ. Your vote decides who gets another week.';
    save();
    render();
  });

  function tick() {
    const left = Math.max(0, state.deadline - Date.now());
    const days = Math.floor(left / 86400000);
    const hours = Math.floor(left % 86400000 / 3600000);
    const mins = Math.floor(left % 3600000 / 60000);
    const secs = Math.floor(left % 60000 / 1000);
    $('days').textContent = String(days).padStart(2, '0');
    $('hours').textContent = String(hours).padStart(2, '0');
    $('minutes').textContent = String(mins).padStart(2, '0');
    $('seconds').textContent = String(secs).padStart(2, '0');
    if (!left) {
      document.querySelectorAll('[data-vote]').forEach(b => { b.disabled = true; b.textContent = 'VOTING HAS CLOSED'; });
      $('vote-message').textContent = state.votes.dj1 === state.votes.dj2
        ? 'The round ended in a tie. An organiser must decide the next step.'
        : `${state.votes.dj1 > state.votes.dj2 ? 'DJ THUKZIN' : 'DJ MAPHO'} survives and stays for another week!`;
    }
  }

  const menu = document.querySelector('.menu-toggle');
  menu.addEventListener('click', () => {
    const open = document.querySelector('.site-header').classList.toggle('menu-open');
    menu.setAttribute('aria-expanded', String(open));
  });
  document.querySelectorAll('.site-header nav a').forEach(a => a.addEventListener('click', () => {
    document.querySelector('.site-header').classList.remove('menu-open');
    menu.setAttribute('aria-expanded', 'false');
  }));

  if (!localStorage.getItem(KEY)) save();
  render();
  tick();
  setInterval(tick, 1000);
})();
