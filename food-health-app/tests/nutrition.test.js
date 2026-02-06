const assert = require('assert');

(async () => {
  const module = await import('../src/utils/nutrition.js');
  const { calculateRecommendedMacros, getRingColor } = module;

  const result = calculateRecommendedMacros(2000);
  assert.strictEqual(result.calories, 2000);
  assert.strictEqual(result.protein, 75);
  assert.strictEqual(result.fat, 66.7);
  assert.strictEqual(result.carb, 275);

  assert.strictEqual(getRingColor(40), '#4CAF50');
  assert.strictEqual(getRingColor(70), '#FF9800');
  assert.strictEqual(getRingColor(110), '#F44336');

  console.log('nutrition test ok');
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
