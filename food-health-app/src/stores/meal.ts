import { defineStore } from 'pinia';
import { API_BASE_URL } from '@/config.js';
import { request } from '@/utils/http';
import reportUtils from '@/utils/report';
import type { DailyNutritionReport, MealRecord } from '@/types/meal';

interface MealState {
    currentDate: string;
    loading: boolean;
    report: DailyNutritionReport | null;
    targetCalories: number | null;
}

export const useMealStore = defineStore('meal', {
    state: (): MealState => ({
        currentDate: new Date().toISOString().split('T')[0],
        loading: false,
        report: null,
        targetCalories: Number(uni.getStorageSync('targetCalories')) || null,
    }),

    getters: {
        // 获取指定餐次的记录
        getMealItems: (state) => (type: string) => {
            if (!state.report?.records) return [];
            return state.report.records.filter(r => r.meal_type?.toLowerCase() === type.toLowerCase());
        },

        // 获取指定餐次的总热量
        getMealCalories: (state) => (type: string) => {
            if (!state.report?.records) return 0;
            const items = state.report.records.filter(r => r.meal_type?.toLowerCase() === type.toLowerCase());
            const sum = items.reduce((acc, cur) => acc + cur.calories, 0);
            return Math.round(sum);
        },

        // 获取今日总热量进度百分比
        caloriePercent(state): number {
            const total = state.report?.total?.calories || 0;
            const recommended = state.targetCalories
                ? state.targetCalories
                : (state.report?.recommended?.calories || 2000);

            if (!recommended) return 0;
            return reportUtils.safePercent(total, recommended);
        },

        // 剩余热量
        remainingCalories(state): number {
            const total = state.report?.total?.calories || 0;
            const recommended = state.targetCalories
                ? state.targetCalories
                : (state.report?.recommended?.calories || 2000);

            const r = recommended - total;
            return r > 0 ? Math.round(r) : 0;
        },

        // 当前使用的推荐目标（优先使用用户自定义的）
        currentRecommended(state) {
            if (state.targetCalories) {
                // 如果有自定义热量，重新计算推荐值（需要引入 nutrition utils，这里简化处理或再次引入）
                // 为了避免循环依赖，建议在组件层处理或者这里引入
                // 简单起见，这里复用 report 中的推荐值结构，但覆盖 calories
                return {
                    ...state.report?.recommended,
                    calories: state.targetCalories
                }
            }
            return state.report?.recommended || { calories: 2000, protein: 75, fat: 66, carb: 275 };
        }
    },

    actions: {
        // 设置当前日期
        setDate(date: string) {
            this.currentDate = date;
            this.fetchDailyReport();
        },

        // 设置目标热量
        setTargetCalories(calories: number | null) {
            this.targetCalories = calories;
            if (calories) {
                uni.setStorageSync('targetCalories', calories);
                uni.setStorageSync('targetCaloriesDate', this.currentDate);
            } else {
                uni.removeStorageSync('targetCalories');
                uni.removeStorageSync('targetCaloriesDate');
            }
        },

        // 获取日报数据
        async fetchDailyReport() {
            const token = uni.getStorageSync('token');
            if (!token) return;

            this.loading = true;
            try {
                const res = await request({
                    url: `${API_BASE_URL}/api/v1/meal/daily-report`,
                    method: 'GET',
                    data: {
                        date: this.currentDate
                    }
                });

                const data = res.data as any;
                if (data && data.code === 0) {
                    this.report = reportUtils.normalizeReport(data.data);
                }
            } catch (e) {
                console.error('Fetch report failed:', e);
                uni.showToast({ title: '加载失败', icon: 'none' });
            } finally {
                this.loading = false;
            }
        },

        // 删除记录
        async deleteRecord(id: number) {
            try {
                const res = await request({
                    url: `${API_BASE_URL}/api/v1/meal/record/${id}`,
                    method: 'DELETE',
                });
                const data = res.data as any;
                if (data && data.code === 0) {
                    // 成功后刷新数据
                    await this.fetchDailyReport();
                    return true;
                }
            } catch (e) {
                uni.showToast({ title: '删除失败', icon: 'none' });
            }
            return false;
        },

        // 更新记录
        async updateRecord(id: number, data: { unit_weight: number, meal_type: string }) {
            try {
                const res = await request({
                    url: `${API_BASE_URL}/api/v1/meal/record/${id}`,
                    method: 'PUT',
                    header: { 'Content-Type': 'application/json' },
                    data
                });

                const resData = res.data as any;
                if (resData && resData.code === 0) {
                    uni.showToast({ title: '已更新' });
                    await this.fetchDailyReport();
                    return true;
                } else {
                    uni.showToast({ title: resData?.message || '更新失败', icon: 'none' });
                }
            } catch (e) {
                uni.showToast({ title: '更新失败', icon: 'none' });
            }
            return false;
        }
    }
});
