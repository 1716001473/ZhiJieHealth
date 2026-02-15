export interface NutritionSummary {
    calories: number;
    protein: number;
    fat: number;
    carb: number;
}

export interface MealRecord {
    id: number;
    user_id: number;
    food_id?: number | null;
    food_name: string;
    image_url?: string | null;
    meal_date: string;
    meal_type: string;
    unit_weight: number;
    note?: string | null;
    calories: number;
    protein: number;
    fat: number;
    carb: number;
}

export interface DailyNutritionReport {
    date: string;
    total: NutritionSummary;
    recommended: NutritionSummary;
    protein_pct: number;
    fat_pct: number;
    carb_pct: number;
    records: MealRecord[];
}
