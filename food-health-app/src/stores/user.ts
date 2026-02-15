import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
    state: () => ({
        token: uni.getStorageSync('token') || '',
        userInfo: uni.getStorageSync('user') || null,
    }),
    getters: {
        isLoggedIn: (state) => !!state.token,
    },
    actions: {
        login(token: string, user: any) {
            this.token = token;
            this.userInfo = user;
            uni.setStorageSync('token', token);
            uni.setStorageSync('user', user);
        },
        logout() {
            this.token = '';
            this.userInfo = null;
            uni.removeStorageSync('token');
            uni.removeStorageSync('user');
        },
        updateUserInfo(user: any) {
            this.userInfo = user;
            uni.setStorageSync('user', user);
        }
    },
});
