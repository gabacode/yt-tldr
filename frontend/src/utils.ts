export const formatTime = (minutes: number, seconds: number): string => {
  if (minutes < 1) return `${Math.round(seconds)}s`;
  return `${minutes.toFixed(2)} min`;
};
