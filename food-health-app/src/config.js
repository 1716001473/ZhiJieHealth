// 开发环境配置
// H5 开发环境下使用空字符串通过 Vite Proxy 转发，其他环境使用完整路径
// 注意：真机调试时需将 localhost 替换为电脑局域网 IP
let baseUrl = 'http://127.0.0.1:8000';

// #ifdef H5
baseUrl = '';
// #endif

// 生产环境配置（部署后需要修改）
// 将下面的 URL 替换为你的 Cloud Run 服务地址
// 例如：let prodBaseUrl = 'https://food-health-api-xxx.tcb.run';
let prodBaseUrl = 'https://your-cloud-run-url.tcb.run';

// 如果是生产环境，使用生产环境地址
if (process.env.NODE_ENV === 'production') {
  baseUrl = prodBaseUrl;
}

export const API_BASE_URL = baseUrl;
export const ALLOW_GUEST_HISTORY = true;
