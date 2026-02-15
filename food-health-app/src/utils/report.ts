import type { DailyNutritionReport, NutritionSummary, MealRecord } from '@/types/meal';

const toNumber = (value: any): number => {
    const num = Number(value);
    return Number.isFinite(num) ? num : 0;
};

/**
 * 安全计算百分比，防止分母为0
 */
export const safePercent = (value: number | string, max: number | string): number => {
    const numerator = toNumber(value);
    const denominator = toNumber(max);
    if (!denominator) return 0;

    const pct = (numerator / denominator) * 100;
    if (!Number.isFinite(pct)) return 0;

    // 限制在 0-100 用于进度条显示（如果需要显示超标，UI层另行处理）
    return Math.min(100, Math.max(0, Math.round(pct)));
};

/**
 * 标准化每日营养报告数据
 * 确保所有字段存在且类型正确
 */
export const normalizeReport = (raw: any): DailyNutritionReport => {
    const defaultRecommended: NutritionSummary = {
        calories: 2000,
        protein: 75,
        fat: 66,
        carb: 275
    };

    const total = raw?.total || {};
    const recommended = raw?.recommended || defaultRecommended;

    return {
        date: raw?.date || new Date().toISOString().split('T')[0],

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

        protein_pct: toNumber(raw?.protein_pct),
        fat_pct: toNumber(raw?.fat_pct),
        carb_pct: toNumber(raw?.carb_pct),

        records: Array.isArray(raw?.records) ? raw.records : []
    } as DailyNutritionReport;
};

export default {
    normalizeReport,
    safePercent
};
