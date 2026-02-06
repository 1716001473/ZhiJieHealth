type RequestOptions = UniApp.RequestOptions & {
  silentAuth?: boolean;
};

const handleUnauthorized = (silent?: boolean) => {
  uni.removeStorageSync('token');
  if (!silent) {
    uni.showToast({ title: '请先登录', icon: 'none' });
  }
  uni.$emit('auth-unauthorized');
};

/**
 * 统一请求封装 - 自动注入 Token
 */
export const request = (options: RequestOptions) => {
  return new Promise<UniApp.RequestSuccessCallbackResult>((resolve, reject) => {
    // 自动注入 Authorization Header
    const token = uni.getStorageSync('token');
    const headers: Record<string, string> = {
      ...(options.header as Record<string, string> || {})
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    uni.request({
      ...options,
      header: headers,
      success: (res) => {
        if (res.statusCode === 401) {
          handleUnauthorized(options.silentAuth);
          resolve(res);
          return;
        }
        resolve(res);
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
};
