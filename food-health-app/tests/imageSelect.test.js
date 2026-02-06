import('../src/utils/imageSelect.js')
  .then(({ buildChooseImageOptions }) => {
    const result = buildChooseImageOptions('camera')
    if (result.count !== 1) {
      throw new Error('image select count should be 1')
    }
    if (!Array.isArray(result.sourceType) || result.sourceType[0] !== 'camera') {
      throw new Error('image select sourceType should include camera')
    }
    if (!Array.isArray(result.sizeType) || result.sizeType[0] !== 'original') {
      throw new Error('image select sizeType should be original')
    }
    console.log('image select test ok')
  })
  .catch((err) => {
    console.error(err)
    process.exit(1)
  })
