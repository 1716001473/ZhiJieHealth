const assert = require('assert');

(async () => {
  const module = await import('../src/utils/planSignature.js');
  const { buildPlanSignature, buildPlanProfilePayload, hasPlanProfileChanged } = module;

  const profile = {
    weight: 68,
    height: 174,
    age: 22,
    gender: 'male',
    activity: 'medium'
  };

  const user = {
    health_goal: 'maintain',
    dietary_preferences: 'vegetarian,low_sugar'
  };

  const signature = buildPlanSignature(profile, user);
  assert.strictEqual(
    signature,
    'weight=68|height=174|age=22|gender=male|activity=medium|goal=maintain|prefs=vegetarian,low_sugar'
  );

  const payload = buildPlanProfilePayload(profile, user);
  assert.deepStrictEqual(payload, {
    health_profile: {
      weight: 68,
      height: 174,
      age: 22,
      gender: 'male',
      activity: 'medium'
    },
    health_goal: 'maintain',
    dietary_preferences: 'vegetarian,low_sugar'
  });

  const sameProfile = { ...profile };
  const sameUser = { ...user };
  assert.strictEqual(hasPlanProfileChanged(profile, user, sameProfile, sameUser), false);

  const updatedProfile = { ...profile, activity: 'high' };
  assert.strictEqual(hasPlanProfileChanged(profile, user, updatedProfile, user), true);

  const updatedUser = { ...user, dietary_preferences: 'vegetarian' };
  assert.strictEqual(hasPlanProfileChanged(profile, user, profile, updatedUser), true);

  console.log('plan signature test ok');
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
