export const shouldShowPlanUpdatePrompt = (savedSignature, currentSignature, needsUpdate) => {
  if (needsUpdate) return true;
  if (!savedSignature) return false;
  return savedSignature !== currentSignature;
};
