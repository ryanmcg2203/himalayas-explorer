(function () {
  const params = new URLSearchParams(window.location.search);
  const defaults = { peak: 'all', metric: 'attempts', split: 'year', view: 'chart' };
  const valid = {
    metric: new Set(['attempts', 'summits', 'rate', 'deaths']),
    split: new Set(['year', 'decade', 'season', 'oxygen', 'staff']),
    view: new Set(['chart', 'table'])
  };

  function applyState() {
    ['metric', 'split'].forEach(name => {
      const value = params.get(name);
      if (value && valid[name].has(value)) document.querySelector('#' + name).value = value;
    });
    const peak = params.get('peak');
    const peakSelect = document.querySelector('#peak');
    if (peak && [...peakSelect.options].some(option => option.value === peak)) peakSelect.value = peak;
    applyView(params.get('view'));
  }

  function applyView(view) {
    const selected = valid.view.has(view) ? view : defaults.view;
    const chart = document.querySelector('#chart-view');
    const table = document.querySelector('#table-view');
    chart.classList.toggle('active', selected === 'chart');
    table.classList.toggle('active', selected === 'table');
    chart.setAttribute('aria-pressed', String(selected === 'chart'));
    table.setAttribute('aria-pressed', String(selected === 'table'));
    document.querySelector('#chart-panel').style.display = selected === 'chart' ? 'block' : 'none';
    document.querySelector('#table-panel').style.display = selected === 'table' ? 'block' : 'none';
  }

  function updateUrl() {
    const next = new URLSearchParams();
    ['peak', 'metric', 'split'].forEach(name => {
      const value = document.querySelector('#' + name).value;
      if (value !== defaults[name]) next.set(name, value);
    });
    const view = document.querySelector('#table-view').classList.contains('active') ? 'table' : 'chart';
    if (view !== defaults.view) next.set('view', view);
    const query = next.toString();
    history.replaceState(null, '', query ? 'index.html?' + query : 'index.html');
  }

  ['metric', 'split', 'peak'].forEach(name => document.querySelector('#' + name).addEventListener('change', updateUrl));
  document.querySelector('#chart-view').addEventListener('click', updateUrl);
  document.querySelector('#table-view').addEventListener('click', updateUrl);
  new MutationObserver(applyState).observe(document.querySelector('#peak'), { childList: true });
  applyState();
}());
