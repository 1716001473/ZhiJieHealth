const requiredFields = ['weight', 'height', 'age', 'gender', 'activity'];

const toNumber = (value) => {
  const num = Number(value);
  return Number.isFinite(num) ? num : 0;
};

const calcBmi = (weight, height) => {
  const w = toNumber(weight);
  const h = toNumber(height);
  if (!w || !h) return 0;
  const meters = h / 100;
  return w / (meters * meters);
};

export const calcBmiValue = (profile) => {
  const bmi = calcBmi(profile?.weight, profile?.height);
  if (!bmi) return 0;
  return Math.round(bmi * 10) / 10;
};

export const getBmiStatus = (bmiValue) => {
  const bmi = toNumber(bmiValue);
  if (!bmi) return '';
  if (bmi < 18.5) return '偏低';
  if (bmi < 24) return '正常';
  if (bmi < 28) return '超重';
  return '肥胖';
};

export const getLocalAdvice = (profile) => {
  const bmi = calcBmiValue(profile);
  if (!bmi) {
    return {
      diet: '完善健康档案后生成饮食建议',
      exercise: '完善健康档案后生成运动建议'
    };
  }
  if (bmi < 18.5) {
    return {
      diet: '适度提高能量密度，主食与优质蛋白安排在三餐，并可加一份健康加餐。',
      exercise: '以轻中度力量训练为主，避免过量有氧造成能量赤字。'
    };
  }
  if (bmi < 24) {
    return {
      diet: '保持均衡饮食，主食粗细搭配，优先选择优质蛋白与新鲜蔬菜。',
      exercise: '维持规律运动，每周至少 3-5 次中等强度锻炼。'
    };
  }
  if (bmi < 28) {
    return {
      diet: '减少精制碳水与油炸食物，用蔬菜和优质蛋白提高饱腹感。',
      exercise: '增加快走、骑行等中等强度运动，提高每日消耗。'
    };
  }
  return {
    diet: '控制总热量摄入，减少夜宵与含糖饮料，三餐以清淡为主。',
    exercise: '优先循序渐进的有氧运动，搭配力量训练提升基础代谢。'
  };
};

export const getDietAdvice = (profile) => {
  return getLocalAdvice(profile).diet;
};

export const calcProfileCompletion = (profile) => {
  const filled = requiredFields.filter((field) => {
    const val = profile?.[field];
    return val !== undefined && val !== null && val !== '';
  }).length;
  return Math.round((filled / requiredFields.length) * 100);
};

export const getHealthFocusMessage = (profile) => {
  const bmi = calcBmiValue(profile);
  if (!bmi) return '完善健康档案，获取个性化建议';
  const status = getBmiStatus(bmi);
  if (status === '超重' || status === '肥胖') return 'BMI 略高，今天清淡一点？';
  if (status === '偏低') return 'BMI 偏低，记得补充能量';
  return 'BMI 正常，保持良好习惯';
};

export default {
  calcBmiValue,
  getBmiStatus,
  getDietAdvice,
  getLocalAdvice,
  calcProfileCompletion,
  getHealthFocusMessage
};
