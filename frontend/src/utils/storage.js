const storage = {
  get(key) {
    try {
      const value = window.localStorage.getItem(key);
      return value === null ? null : JSON.parse(value);
    } catch {
      return null;
    }
  },

  set(key, value) {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch {
      return false;
    }
  },
};

export default storage;
