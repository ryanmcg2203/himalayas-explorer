let peaks = [], expeditions = [];
const $ = selector => document.querySelector(selector);
const fmt = value => Number(value || 0).toLocaleString();
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
const seasonNames = { 1: 'Spring', 2: 'Summer', 3: 'Autumn', 4: 'Winter' };
const params = new URLSearchParams(location.search);

function peakById(id) { return peaks.find(peak => peak.peakId === id) || peaks[0]; }
function rowsFor(peak) { return expeditions.filter(row => row.peakId === peak.peakId); }
function rate(peak) { return peak.memberSummitRate == null ? '—' : peak.memberSummitRate.toFixed(1) + '%'; }
function optionList(select) {
  peaks.slice().sort((a, b) => a.name.localeCompare(b.name)).forEach(peak => {
    const option = document.createElement('option'); option.value = peak.peakId; option.textContent = peak.name; select.appendChild(option);
  });
}
function updateUrl(left, right) { history.replaceState(null, '', 'compare.html?left=' + encodeURIComponent(left.peakId) + '&right=' + encodeURIComponent(right.peakId)); }
function render() {
  const left = peakById($('#left-peak').value), right = peakById($('#right-peak').value);
  if (!left || !right) return;
  updateUrl(left, right);
  [['left', left], ['right', right]].forEach(([prefix, peak]) => {
    $( '#' + prefix + '-label').textContent = peak.peakId;
    $( '#' + prefix + '-name').innerHTML = '<a href="peak.html?peak=' + encodeURIComponent(peak.peakId) + '">' + esc(peak.name) + '</a>';
    $( '#' + prefix + '-meta').textContent = [peak.heightM ? fmt(peak.heightM) + ' m' : 'Height not recorded', peak.location || 'Location not recorded'].join(' · ');
    $( '#' + prefix + '-expeditions').textContent = fmt(peak.expeditions);
    $( '#' + prefix + '-rate').textContent = rate(peak);
    $( '#' + prefix + '-deaths').textContent = fmt(peak.deaths);
  });
  $('#left-column').innerHTML = '<a href="peak.html?peak=' + encodeURIComponent(left.peakId) + '">' + esc(left.name) + '</a>'; $('#right-column').innerHTML = '<a href="peak.html?peak=' + encodeURIComponent(right.peakId) + '">' + esc(right.name) + '</a>';
  $('#left-decade').innerHTML = '<a href="peak.html?peak=' + encodeURIComponent(left.peakId) + '">' + esc(left.name) + '</a>'; $('#right-decade').innerHTML = '<a href="peak.html?peak=' + encodeURIComponent(right.peakId) + '">' + esc(right.name) + '</a>';
  const measures = [['Member attempts', left.memberAttempts, right.memberAttempts], ['Member summits', left.memberSummits, right.memberSummits], ['Member summit rate', rate(left), rate(right)], ['Member deaths', left.memberDeaths, right.memberDeaths], ['Hired deaths', left.hiredDeaths, right.hiredDeaths], ['All deaths', left.deaths, right.deaths]];
  $('#detail-rows').innerHTML = measures.map(row => '<tr><td>' + row[0] + '</td><td>' + (typeof row[1] === 'number' ? fmt(row[1]) : row[1]) + '</td><td>' + (typeof row[2] === 'number' ? fmt(row[2]) : row[2]) + '</td></tr>').join('');
  const leftRows = rowsFor(left), rightRows = rowsFor(right), decades = [...new Set([...leftRows, ...rightRows].map(row => Math.floor(row.year / 10) * 10))].sort((a, b) => a - b);
  $('#decade-rows').innerHTML = decades.map(decade => '<tr><td>' + decade + 's</td><td>' + fmt(leftRows.filter(row => Math.floor(row.year / 10) * 10 === decade).length) + '</td><td>' + fmt(rightRows.filter(row => Math.floor(row.year / 10) * 10 === decade).length) + '</td></tr>').join('');
  const seasonRows = [1, 2, 3, 4].map(season => ({ season, left: leftRows.filter(row => row.season === season).length, right: rightRows.filter(row => row.season === season).length }));
  const maxSeason = Math.max(1, ...seasonRows.flatMap(row => [row.left, row.right]));
  $('#season-rows').innerHTML = seasonRows.map(row => '<div class="season"><label>' + seasonNames[row.season] + '</label><div class="bars"><div class="bar" style="width:' + row.left / maxSeason * 100 + '%"></div><div class="bar right" style="width:' + row.right / maxSeason * 100 + '%"></div></div><strong>' + row.left + ' / ' + row.right + '</strong></div>').join('');
  $('#comparison').hidden = false;
}
function showError(message) { $('#error').hidden = false; $('#error').textContent = message; }

Promise.all([fetch('peaks.json'), fetch('expeditions.json')]).then(async responses => {
  if (responses.some(response => !response.ok)) throw Error('Comparison data is unavailable');
  return Promise.all(responses.map(response => response.json()));
}).then(([peakRows, expeditionRows]) => {
  peaks = peakRows; expeditions = expeditionRows;
  optionList($('#left-peak')); optionList($('#right-peak'));
  const left = peakById(params.get('left') || 'EVER'), right = peakById(params.get('right') || 'AMAD');
  $('#left-peak').value = left.peakId; $('#right-peak').value = right.peakId;
  $('#left-peak').addEventListener('change', render); $('#right-peak').addEventListener('change', render);
  render();
}).catch(error => showError(error.message + '. Run the local data build first.'));
