const assert = require('assert');

(async () => {
  const module = await import('../src/utils/planRecommendation.js');
  const { shouldShowPlanUpdatePrompt } = module;

  assert.strictEqual(shouldShowPlanUpdatePrompt('', 'a', false), false);
  assert.strictEqual(shouldShowPlanUpdatePrompt('a', 'a', false), false);
  assert.strictEqual(shouldShowPlanUpdatePrompt('a', 'b', false), true);
  assert.strictEqual(shouldShowPlanUpdatePrompt('a', 'a', true), true);

  console.log('plan recommendation helper test ok');
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
