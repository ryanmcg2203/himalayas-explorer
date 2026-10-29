const originalPeaksComparator = comparator;
comparator = function (a, b) {
  if (sortKey === 'name' || sortKey === 'trend') return originalPeaksComparator(a, b);
  const field = sortKey === 'height' ? 'heightM' : sortKey === 'rate' ? 'memberSummitRate' : sortKey;
  const av = a[field], bv = b[field];
  if (av == null && bv == null) return a.name.localeCompare(b.name);
  if (av == null) return 1;
  if (bv == null) return -1;
  return (av - bv) * sortDirection || a.name.localeCompare(b.name);
};

const originalPeaksApplyState = applyState;
applyState = function () {
  originalPeaksApplyState();
  if (params().get('direction') === 'asc') sortDirection = 1;
  if (params().get('direction') === 'desc') sortDirection = -1;
};
