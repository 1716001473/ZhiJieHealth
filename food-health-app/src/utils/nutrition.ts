import type { NutritionSummary } from '@/types/meal';

const round1 = (value: number): number => Math.round(value * 10) / 10;

/**
 * 根据目标热量计算推荐的三大营养素
 * @param targetCalories 每日目标热量 (kcal)
 */
export const calculateRecommendedMacros = (targetCalories: number | string): NutritionSummary => {
    const calories = Number(targetCalories) || 0;
    // 蛋白质 15% (1g = 4kcal)
    const protein = round1((calories * 0.15) / 4);
    // 脂肪 30% (1g = 9kcal)
    const fat = round1((calories * 0.3) / 9);
    // 碳水 55% (1g = 4kcal)
    const carb = round1((calories * 0.55) / 4);

    return {
        calories: Math.round(calories), // 热量取整
        protein,
        fat,
        carb
    };
};

/**
 * 根据百分比获取圆环颜色
 * @param percent 进度百分比 (0-100+)
 */
export const getRingColor = (percent: number | string): string => {
    const value = Number(percent) || 0;
    if (value >= 100) return '#F44336'; // 红色 - 超标
    if (value >= 60) return '#FF9800'; // 橙色 - 接近
    return '#4CAF50'; // 绿色 - 正常
};

export default {
    calculateRecommendedMacros,
    getRingColor
};
