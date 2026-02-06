export const DEFAULT_IMAGE_SIZE_TYPE = ['original']
export const DEFAULT_IMAGE_COUNT = 1

export const buildChooseImageOptions = (source) => ({
  count: DEFAULT_IMAGE_COUNT,
  sourceType: [source],
  sizeType: DEFAULT_IMAGE_SIZE_TYPE,
})
