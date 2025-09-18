import { appReducer } from "slices/reducers/appReducer";

export default (state, action) => {
  return appReducer(state, action);
};
