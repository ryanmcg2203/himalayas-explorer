const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const context = { window: {} };
vm.runInNewContext(fs.readFileSync('dist/metrics.js', 'utf8'), context);
const metrics = context.window.HimalayasMetrics;
const row = {
  year: 1922, teamMembers: 7, hiredStaff: 14, participants: 21,
  memberSummiters: 2, summiters: 5, summitHired: 3, deaths: 9, memberDeaths: 1,
  hiredDeaths: 8, disputed: true
};

assert.equal(JSON.stringify(metrics.modeMetrics(row, 'members')), JSON.stringify({ attempts: 7, summits: 2, deaths: 1 }));
assert.equal(JSON.stringify(metrics.modeMetrics(row, 'hired')), JSON.stringify({ attempts: 14, summits: 3, deaths: 8 }));
assert.equal(JSON.stringify(metrics.modeMetrics(row, 'all')), JSON.stringify({ attempts: 21, summits: 5, deaths: 9 }));
assert.equal(metrics.seasonLabel(null), 'Unknown');
assert.equal(JSON.stringify(metrics.aggregatePeakYears([row], 'members')[0]), JSON.stringify({
  year: 1922, expeditions: 1, summits: 2, deaths: 1, attempts: 7, disputed: 1
}));
console.log('metrics fixtures passed');
