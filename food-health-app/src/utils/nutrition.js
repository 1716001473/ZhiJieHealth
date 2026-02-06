const round1 = (value) => Math.round(value * 10) / 10;

export const calculateRecommendedMacros = (targetCalories) => {
  const calories = Number(targetCalories) || 0;
  const protein = round1((calories * 0.15) / 4);
  const fat = round1((calories * 0.3) / 9);
  const carb = round1((calories * 0.55) / 4);
  return {
    calories,
    protein,
    fat,
    carb
  };
};

export const getRingColor = (percent) => {
  const value = Number(percent) || 0;
  if (value >= 100) return '#F44336';
  if (value >= 60) return '#FF9800';
  return '#4CAF50';
};

export default {
  calculateRecommendedMacros,
  getRingColor
};
