const assert = require('assert');

(async () => {
  const module = await import('../src/utils/healthProfile.js');
  const {
    calcProfileCompletion,
    getHealthFocusMessage,
    calcBmiValue,
    getBmiStatus,
    getDietAdvice,
    getLocalAdvice
  } = module;

  const profile = {
    weight: 65,
    height: 170,
    age: 28,
    gender: 'male',
    activity: 'medium'
  };

  assert.strictEqual(calcProfileCompletion(profile), 100);

  const partial = { weight: 65, height: 170 };
  assert.strictEqual(calcProfileCompletion(partial), 40);

  const msg = getHealthFocusMessage({ weight: 80, height: 170 });
  assert.ok(msg.includes('BMI'));

  const bmiValue = calcBmiValue({ weight: 67, height: 174 });
  assert.ok(Math.abs(bmiValue - 22.1) < 0.2);
  assert.strictEqual(getBmiStatus(17.5), '偏低');
  assert.strictEqual(getBmiStatus(22), '正常');
  assert.strictEqual(getBmiStatus(25), '超重');
  assert.strictEqual(getBmiStatus(30), '肥胖');

  const adviceLow = getDietAdvice({ weight: 45, height: 170 });
  assert.ok(adviceLow.includes('能量'));
  const adviceHigh = getDietAdvice({ weight: 90, height: 170 });
  assert.ok(adviceHigh.includes('热量'));
  const adviceNone = getDietAdvice({ weight: '', height: '' });
  assert.ok(adviceNone.includes('完善'));

  const localAdvice = getLocalAdvice({ weight: 65, height: 170 });
  assert.ok(localAdvice.diet.includes('均衡'));
  assert.ok(localAdvice.exercise.includes('运动'));

  console.log('health profile test ok');
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
