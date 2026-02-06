// H5 开发环境下使用空字符串通过 Vite Proxy 转发，其他环境使用完整路径
// 注意：真机调试时需将 localhost 替换为电脑局域网 IP
let baseUrl = 'http://127.0.0.1:8000';

// #ifdef H5
baseUrl = '';
// #endif

export const API_BASE_URL = baseUrl;
export const ALLOW_GUEST_HISTORY = true;
