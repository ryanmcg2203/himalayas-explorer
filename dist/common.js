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
})(window);
