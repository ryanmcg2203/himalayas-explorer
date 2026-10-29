const originalGroupData = groupData;
groupData = function (data) {
  const groups = originalGroupData(data);
  if ($('#split').value !== 'season') return groups;
  const order = { Spring: 1, Summer: 2, Autumn: 3, Winter: 4, 'Season not recorded': 99, Unknown: 99 };
  return groups.sort((a, b) => (order[a.label] ?? 99) - (order[b.label] ?? 99));
};
