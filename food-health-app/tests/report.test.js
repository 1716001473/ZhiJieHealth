const assert = require('assert');

(async () => {
  const module = await import('../src/utils/report.js');
  const { normalizeReport, safePercent } = module;

  const report = normalizeReport({
    total: { calories: null, protein: undefined, fat: '1.5', carb: 0 },
    recommended: null,
    records: []
  });

  assert.strictEqual(report.total.calories, 0);
  assert.strictEqual(report.total.protein, 0);
  assert.strictEqual(report.total.fat, 1.5);
  assert.strictEqual(report.recommended.calories, 2000);

  assert.strictEqual(safePercent(50, 0), 0);
  assert.strictEqual(safePercent(50, 100), 50);
  assert.strictEqual(safePercent(200, 100), 100);

  console.log('report test ok');
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
