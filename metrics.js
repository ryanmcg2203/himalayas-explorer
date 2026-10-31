(function (global) {
  const expeditionFields = [
    'id', 'year', 'mountain', 'peakId', 'teamMembers', 'hiredStaff',
    'participants', 'summiters', 'summitHired', 'memberSummiters',
    'deaths', 'memberDeaths', 'hiredDeaths', 'season', 'disputed',
    'route', 'route2', 'route3', 'route4', 'routeNormalized',
    'route2Normalized', 'route3Normalized', 'route4Normalized'
  ];

  function assertFields(rows, fields, label) {
    const missing = fields.filter(field => rows.some(row => !Object.prototype.hasOwnProperty.call(row, field)));
    if (missing.length) throw new Error(label + ' is missing required fields: ' + missing.join(', '));
  }

  function assertExpeditions(rows) {
    assertFields(rows, expeditionFields, 'Expedition export');
  }

  function modeMetrics(row, mode) {
    if (mode === 'hired') return { attempts: Number(row.hiredStaff), summits: Number(row.summitHired), deaths: Number(row.hiredDeaths) };
    if (mode === 'all') return { attempts: Number(row.participants), summits: Number(row.summiters), deaths: Number(row.deaths) };
    return { attempts: Number(row.teamMembers), summits: Number(row.memberSummiters), deaths: Number(row.memberDeaths) };
  }

  function seasonLabel(value) {
    return ({ 1: 'Spring', 2: 'Summer', 3: 'Autumn', 4: 'Winter' })[value] || 'Unknown';
  }

  function routeKey(value) {
    return String(value || '').trim().replace(/\s+/g, ' ').toLowerCase();
  }

  function aggregatePeakYears(rows, mode) {
    const byYear = {};
    rows.forEach(row => {
      const metrics = modeMetrics(row, mode);
      const year = byYear[row.year] || (byYear[row.year] = {
        year: row.year, expeditions: 0, summits: 0, deaths: 0,
        attempts: 0, disputed: 0
      });
      year.expeditions += 1;
      year.summits += metrics.summits;
      year.deaths += metrics.deaths;
      year.attempts += metrics.attempts;
      year.disputed += row.disputed ? 1 : 0;
    });
    return Object.values(byYear);
  }

  global.HimalayasMetrics = { expeditionFields, assertExpeditions, modeMetrics, seasonLabel, routeKey, aggregatePeakYears };
})(window);
