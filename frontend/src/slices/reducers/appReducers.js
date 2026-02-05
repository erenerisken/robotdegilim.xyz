import { combineReducers } from "redux";

import dontFillsReducer from "../dontFillsSlice";
import scenariosReducer from "../scenariosSlice";
import themeReducer from "../themeSlice";

export const appReducer = combineReducers({
  dontFillsState: dontFillsReducer,
  scenariosState: scenariosReducer,
  themeState: themeReducer,
});
