export const validateDescription = (description: string): string | null => {
  if (!description || description.trim().length < 10) {
    return 'Description must be at least 10 characters';
  }
  if (description.length > 2000) {
    return 'Description must be less than 2000 characters';
  }
  return null;
};

export const validateLength = (length: number): string | null => {
  if (length < 500) {
    return 'Document length must be at least 500 words';
  }
  if (length > 5000) {
    return 'Document length must not exceed 5000 words';
  }
  return null;
};

export const validateStatistic = (
  name: string,
  value: number,
  unit?: string
): string | null => {
  if (!name || name.trim().length === 0) {
    return 'Statistic name is required';
  }
  if (name.length > 100) {
    return 'Statistic name must be less than 100 characters';
  }
  if (isNaN(value)) {
    return 'Statistic value must be a number';
  }
  if (unit && unit.length > 20) {
    return 'Unit must be less than 20 characters';
  }
  return null;
};

export const validateFile = (file: File): string | null => {
  const maxSize = parseInt(import.meta.env.VITE_MAX_FILE_SIZE || '5242880');
  const allowedFormats = (
    import.meta.env.VITE_SUPPORTED_FORMATS || 'image/png,image/jpeg,image/svg+xml'
  ).split(',');

  if (file.size > maxSize) {
    return `File size must be less than ${(maxSize / 1024 / 1024).toFixed(1)}MB`;
  }

  if (!allowedFormats.includes(file.type)) {
    return 'Invalid file format. Allowed: PNG, JPG, SVG';
  }

  return null;
};
