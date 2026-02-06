const toNumber = (value) => {
  const num = Number(value);
  return Number.isFinite(num) ? num : 0;
};

export const safePercent = (value, max) => {
  const numerator = toNumber(value);
  const denominator = toNumber(max);
  if (!denominator) return 0;
  const pct = (numerator / denominator) * 100;
  if (!Number.isFinite(pct)) return 0;
  return Math.min(100, Math.max(0, Math.round(pct)));
};

export const normalizeReport = (raw) => {
  const defaultRecommended = { calories: 2000, protein: 75, fat: 66, carb: 275 };
  const total = raw?.total || {};
  const recommended = raw?.recommended || defaultRecommended;

  return {
    ...raw,
    total: {
      calories: toNumber(total.calories),
      protein: toNumber(total.protein),
      fat: toNumber(total.fat),
      carb: toNumber(total.carb)
    },
    recommended: {
      calories: toNumber(recommended.calories || defaultRecommended.calories),
      protein: toNumber(recommended.protein || defaultRecommended.protein),
      fat: toNumber(recommended.fat || defaultRecommended.fat),
      carb: toNumber(recommended.carb || defaultRecommended.carb)
    },
    records: Array.isArray(raw?.records) ? raw.records : []
  };
};

export default {
  normalizeReport,
  safePercent
};
