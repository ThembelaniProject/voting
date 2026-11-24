(() => {
  const battle = document.getElementById('battle');
  const competitionId = battle.dataset.competitionId;
  const votingOpenOnPage = battle.dataset.votingOpen === 'true';
  const deadline = Date.parse(battle.dataset.deadline || '') || 0;
  const $ = id => document.getElementById(id);
  const fmt = value => Number(value || 0).toLocaleString('en-ZA');
  let alreadyVoted = false;
  let votingOpen = votingOpenOnPage;
  let submitting = false;

  function csrfToken() {
    const entry = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    return entry ? decodeURIComponent(entry.split('=').slice(1).join('=')) : '';
  }

  function render(data) {
    if (data) {
      $('dj1-votes').textContent = fmt(data.dj1);
      $('dj2-votes').textContent = fmt(data.dj2);
      $('total-votes').textContent = fmt(data.total);
      $('leader-one').textContent = fmt(data.dj1);
      $('leader-two').textContent = fmt(data.dj2);
      $('dj1-percent').textContent = `${Number(data.dj1_percent || 0).toFixed(1)}%`;
      $('dj2-percent').textContent = `${Number(data.dj2_percent || 0).toFixed(1)}%`;
      $('dj1-bar').style.width = `${data.dj1_percent || 0}%`;
      $('dj2-bar').style.width = `${data.dj2_percent || 0}%`;
      if (typeof data.voting_open === 'boolean') votingOpen = data.voting_open;
      if (typeof data.already_voted === 'boolean') alreadyVoted = data.already_voted;
    }

    document.querySelectorAll('[data-vote]').forEach(button => {
      button.disabled = submitting || alreadyVoted || !votingOpen || !competitionId;
      if (alreadyVoted) button.textContent = 'VOTE ALREADY SUBMITTED';
      else if (!votingOpen) button.textContent = 'VOTING IS NOT OPEN';
      else if (button.dataset.vote === 'dj1') button.textContent = 'I WANT THIS DJ TO STAY ↗';
      else button.textContent = 'I WANT THIS DJ TO STAY ↗';
    });

    if (alreadyVoted) {
      $('vote-message').textContent = 'Thank you. Your vote has been recorded for this weekly competition.';
      $('vote-status').textContent = 'Your vote is recorded';
    } else if (!votingOpen) {
      $('vote-message').textContent = 'Voting is not open right now. Check back when Pheli FM opens the round.';
      $('vote-status').textContent = 'Voting closed';
    } else {
      $('vote-message').textContent = 'Choose the DJ you want to keep in the competition.';
      $('vote-status').textContent = 'Live results · updates automatically';
    }
  }

  async function refreshStats() {
    if (!competitionId) {
      render(null);
      return;
    }
    try {
      const response = await fetch(`/api/competitions/${competitionId}/stats/`, {
        method: 'GET',
        credentials: 'same-origin',
        headers: { 'Accept': 'application/json' }
      });
      if (!response.ok) throw new Error('Could not load current vote totals.');
      render(await response.json());
    } catch (error) {
      $('vote-status').textContent = 'Live results temporarily unavailable';
    }
  }

  async function submitVote(choice, button) {
    if (!competitionId || submitting || alreadyVoted || !votingOpen) return;
    submitting = true;
    render(null);
    button.textContent = 'SUBMITTING VOTE…';
    try {
      const response = await fetch(`/api/competitions/${competitionId}/vote/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'X-CSRFToken': csrfToken()
        },
        body: JSON.stringify({ choice })
      });
      const result = await response.json();
      if (!response.ok) {
        if (response.status === 409) alreadyVoted = true;
        if (response.status === 403) votingOpen = false;
        throw new Error(result.error || 'Your vote could not be submitted.');
      }
      alreadyVoted = true;
      votingOpen = true;
      render(result);
      $('vote-confirm').hidden = false;
      $('vote-confirm').textContent = result.message;
    } catch (error) {
      $('vote-message').textContent = error.message;
      await refreshStats();
    } finally {
      submitting = false;
      render(null);
    }
  }

  document.querySelectorAll('[data-vote]').forEach(button => {
    button.addEventListener('click', () => submitVote(button.dataset.vote, button));
  });

  function tick() {
    const left = Math.max(0, deadline - Date.now());
    const days = Math.floor(left / 86400000);
    const hours = Math.floor(left % 86400000 / 3600000);
    const mins = Math.floor(left % 3600000 / 60000);
    const secs = Math.floor(left % 60000 / 1000);
    $('days').textContent = String(days).padStart(2, '0');
    $('hours').textContent = String(hours).padStart(2, '0');
    $('minutes').textContent = String(mins).padStart(2, '0');
    $('seconds').textContent = String(secs).padStart(2, '0');
    if (!left && votingOpen) {
      votingOpen = false;
      render(null);
    }
  }

  const menu = document.querySelector('.menu-toggle');
  menu.addEventListener('click', () => {
    const open = document.querySelector('.site-header').classList.toggle('menu-open');
    menu.setAttribute('aria-expanded', String(open));
  });
  document.querySelectorAll('.site-header nav a').forEach(link => link.addEventListener('click', () => {
    document.querySelector('.site-header').classList.remove('menu-open');
    menu.setAttribute('aria-expanded', 'false');
  }));

  refreshStats();
  tick();
  window.setInterval(tick, 1000);
  window.setInterval(refreshStats, 10000);
})();
