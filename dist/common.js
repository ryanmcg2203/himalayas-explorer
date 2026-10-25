(function (global) {
  const seasonNames = { 1: 'Spring', 2: 'Summer', 3: 'Autumn', 4: 'Winter' };
  function bool(value) {
    if (typeof value === 'string') return ['1', 'true', 'y', 'yes'].includes(value.trim().toLowerCase());
    return value === true || value === 1;
  }
  function seasonLabel(value) { return seasonNames[value] || 'Season not recorded'; }
  function oxygenLabel(value) { return value === true ? 'Yes' : value === false ? 'No' : 'Not recorded'; }
  function esc(value) { return String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char])); }
  function fmt(value) { return Number(value || 0).toLocaleString(); }
  global.HimalayasCommon = { bool, seasonLabel, oxygenLabel, esc, fmt };
  const tableBody = document.querySelector('#table-body');
  if (tableBody) {
    const headers = [...tableBody.closest('table').querySelectorAll('thead th')];
    let sortedColumn = -1;
    let sortDirection = 1;
    const sortTable = column => {
      if (sortedColumn === column) sortDirection *= -1;
      else { sortedColumn = column; sortDirection = 1; }
      [...tableBody.rows].sort((a, b) => {
        const av = a.cells[column].textContent.trim();
        const bv = b.cells[column].textContent.trim();
        const an = Number.parseFloat(av.replace(/[^0-9.-]/g, ''));
        const bn = Number.parseFloat(bv.replace(/[^0-9.-]/g, ''));
        const result = Number.isNaN(an) || Number.isNaN(bn) ? av.localeCompare(bv) : an - bn;
        return (result || a.cells[0].textContent.localeCompare(b.cells[0].textContent)) * sortDirection;
      }).forEach(row => tableBody.appendChild(row));
      headers.forEach((header, index) => {
        header.tabIndex = 0;
        header.style.cursor = 'pointer';
        header.setAttribute('aria-sort', index === sortedColumn ? (sortDirection > 0 ? 'ascending' : 'descending') : 'none');
      });
    };
    headers.forEach((header, index) => {
      header.addEventListener('click', () => sortTable(index));
      header.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); sortTable(index); }
      });
    });
  }
  const textWalker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (textWalker.nextNode()) {
    const node = textWalker.currentNode;
    if (!node.parentElement.closest('script,style')) {
      node.nodeValue = node.nodeValue.replace(/Loading local data…/g, 'Loading data…').replace(/ · local derived data/g, '');
    }
  }
  const chart = document.querySelector('#chart');
  if (chart) {
    const style = document.createElement('style');
    style.textContent = '.bar-tip{min-width:170px;max-width:220px;white-space:normal;text-align:left;padding:10px 12px;line-height:1.35}.bar-tip strong,.bar-tip b,.bar-tip span{display:block}.bar-tip strong{font-size:12px}.bar-tip b{color:#17605d;font-size:13px;margin-top:3px}.bar-tip span{border-top:1px solid #b8d4ce;margin-top:7px;padding-top:7px;color:#46635f;font-size:11px}';
    document.head.appendChild(style);
    const formatTips = () => chart.querySelectorAll('.bar-tip').forEach(tip => {
      if (tip.dataset.formatted) return;
      const parts = tip.textContent.split(' · ');
      if (parts.length < 2) return;
      const detail = parts.slice(2).join(' · ');
      const definition = parts[1].toLowerCase().includes('rate') ? 'Member summits ÷ member attempts.' : '';
      tip.innerHTML = '<strong>' + esc(parts[0]) + '</strong><b>' + esc(parts[1]) + '</b>' + (detail ? '<span>' + esc(detail) + '</span>' : '');
      if (definition) tip.querySelector('span').textContent += ' ' + definition;
      tip.dataset.formatted = 'true';
    });
    const repairRateYearSpine = () => {
      const split = document.querySelector('#split');
      const metric = document.querySelector('#metric');
      if (!split || !metric || split.value !== 'year' || metric.value !== 'rate') return;
      const bars = chart.querySelector('.bars');
      if (!bars) { delete chart.dataset.spineKey; return; }
      const columns = [...bars.querySelectorAll('.bar-col')];
      const years = columns.map(column => Number.parseInt(column.querySelector('.bar-tip')?.textContent || '', 10)).filter(Number.isFinite);
      const range = document.querySelector('#chart-subtitle')?.textContent.match(/(\d{4})–(\d{4})/);
      if (!range || !years.length) return;
      const first = Number(range[1]), last = Number(range[2]), key = first + '-' + last + '-' + columns.length;
      if (chart.dataset.spineKey === key || last - first > 250) return;
      const byYear = new Map(columns.map(column => [Number.parseInt(column.querySelector('.bar-tip')?.textContent || '', 10), column]));
      const fragment = document.createDocumentFragment();
      for (let year = first; year <= last; year += 1) {
        const column = byYear.get(year) || document.createElement('div');
        if (!column.className) { column.className = 'bar-col'; column.setAttribute('aria-label', year + ' · no member attempts'); }
        fragment.appendChild(column);
      }
      bars.replaceChildren(fragment);
      chart.dataset.spineKey = key;
    };
    const repairChart = () => { formatTips(); repairRateYearSpine(); };
    new MutationObserver(repairChart).observe(chart, { childList: true, subtree: true });
  }
  if (document.querySelector('#search') && document.querySelector('#result')) {
    const replace = history.replaceState.bind(history);
    let typing = false;
    const searchUrl = value => {
      const url = new URL(location.href);
      if (value) url.searchParams.set('q', value);
      else url.searchParams.delete('q');
      return url.pathname + (url.searchParams.toString() ? '?' + url.searchParams : '') + url.hash;
    };
    const commitSearch = () => {
      const input = document.querySelector('#search');
      if (!input) return;
      replace(history.state, '', searchUrl(input.value.trim()));
      typing = false;
    };
    document.addEventListener('input', event => {
      if (event.target.matches('#search')) typing = true;
    }, true);
    document.addEventListener('change', () => {
      if (typing) commitSearch();
    }, true);
    document.addEventListener('keydown', event => {
      if (typing && event.target.matches('#search') && event.key === 'Enter') commitSearch();
    }, true);
    history.replaceState = function (state, title, url) {
      if (typing && url) {
        const next = new URL(url, location.href);
        next.searchParams.delete('q');
        return replace(state, title, next.pathname + (next.searchParams.toString() ? '?' + next.searchParams : '') + next.hash);
      }
      return replace(state, title, url);
    };
  }
})(window);
