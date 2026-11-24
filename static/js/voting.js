(() => {
  const battle = document.getElementById('battle');
  const week = battle.dataset.week || '0';
  const KEY = `pheli-fm-950-dj-survival-week-${week}`;
  const votingOpen = battle.dataset.votingOpen === 'true';
  const configuredDeadline = Date.parse(battle.dataset.deadline || '') || 0;
  const seed = { dj1: 0, dj2: 0 };
  const $ = id => document.getElementById(id);
  const freshState = () => ({ votes: {...seed}, votedFor: null, deadline: configuredDeadline });
  const readState = () => {
    try {
      const saved = JSON.parse(localStorage.getItem(KEY));
      return saved && saved.votes && typeof saved.deadline === 'number' ? saved : freshState();
    } catch { return freshState(); }
  };
  let state = readState();
  const save = () => localStorage.setItem(KEY, JSON.stringify(state));
  const fmt = n => Number(n).toLocaleString('en-ZA');

  function render() {
    const total = state.votes.dj1 + state.votes.dj2;
    const p1 = total ? state.votes.dj1 / total * 100 : 0;
    const p2 = total ? 100 - p1 : 0;
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
      const ended = !votingOpen || !state.deadline || Date.now() >= state.deadline;
      btn.disabled = Boolean(state.votedFor) || ended;
      if (state.votedFor) btn.textContent = state.votedFor === btn.dataset.vote ? 'YOUR DEMO VOTE IS CAST ✓' : 'DEMO VOTE ALREADY CAST';
      else if (ended) btn.textContent = 'VOTING IS NOT OPEN';
    });
    if (state.votedFor) {
      $('vote-message').textContent = 'Thanks for supporting your DJ. This browser has used its demo vote for this round.';
      $('vote-confirm').hidden = false;
      $('vote-confirm').textContent = `Your demo vote for ${state.votedFor === 'dj1' ? $('dj1-name').textContent : $('dj2-name').textContent} has been saved in this browser only.`;
    } else if (!votingOpen) {
      $('vote-message').textContent = 'Voting is not open right now. Pheli FM will announce when the next round begins.';
    }
  }

  document.querySelectorAll('[data-vote]').forEach(btn => btn.addEventListener('click', () => {
    if (!votingOpen || state.votedFor || !state.deadline || Date.now() >= state.deadline) return;
    state.votes[btn.dataset.vote] += 1;
    state.votedFor = btn.dataset.vote;
    save();
    render();
  }));

  $('reset-demo').addEventListener('click', () => {
    localStorage.removeItem(KEY);
    state = freshState();
    $('vote-confirm').hidden = true;
    $('vote-message').textContent = votingOpen
      ? 'Pick ONE DJ. Your vote decides who gets another week.'
      : 'Voting is not open right now. Pheli FM will announce when the next round begins.';
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
    if (!left || !votingOpen) {
      document.querySelectorAll('[data-vote]').forEach(b => { b.disabled = true; b.textContent = 'VOTING IS NOT OPEN'; });
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
