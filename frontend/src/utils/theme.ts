export type AppTheme = 'light' | 'dark';

const THEME_STORAGE_KEY = 'app-theme';

const isTheme = (value: string | null): value is AppTheme => value === 'light' || value === 'dark';

export const getStoredTheme = (): AppTheme => {
  const storedValue = localStorage.getItem(THEME_STORAGE_KEY);
  return isTheme(storedValue) ? storedValue : 'light';
};

export const applyTheme = (theme: AppTheme) => {
  document.documentElement.dataset.theme = theme;
  document.documentElement.classList.toggle('dark-theme', theme === 'dark');
  localStorage.setItem(THEME_STORAGE_KEY, theme);
};

export const initializeTheme = () => {
  applyTheme(getStoredTheme());
};