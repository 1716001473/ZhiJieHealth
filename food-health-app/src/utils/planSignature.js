const normalizeValue = (value) => {
  if (value === undefined || value === null) return '';
  return String(value);
};

export const buildPlanSignature = (profile = {}, user = {}) => {
  const weight = normalizeValue(profile.weight);
  const height = normalizeValue(profile.height);
  const age = normalizeValue(profile.age);
  const gender = normalizeValue(profile.gender);
  const activity = normalizeValue(profile.activity);
  const goal = normalizeValue(user.health_goal);
  const prefs = normalizeValue(user.dietary_preferences);

  return [
    `weight=${weight}`,
    `height=${height}`,
    `age=${age}`,
    `gender=${gender}`,
    `activity=${activity}`,
    `goal=${goal}`,
    `prefs=${prefs}`
  ].join('|');
};

export const buildPlanProfilePayload = (profile = {}, user = {}) => {
  return {
    health_profile: {
      weight: profile.weight,
      height: profile.height,
      age: profile.age,
      gender: profile.gender,
      activity: profile.activity
    },
    health_goal: user.health_goal || '',
    dietary_preferences: user.dietary_preferences || ''
  };
};

export const hasPlanProfileChanged = (prevProfile = {}, prevUser = {}, nextProfile = {}, nextUser = {}) => {
  const prevSignature = buildPlanSignature(prevProfile, prevUser);
  const nextSignature = buildPlanSignature(nextProfile, nextUser);
  return prevSignature !== nextSignature;
};
