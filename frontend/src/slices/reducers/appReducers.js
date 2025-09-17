import { combineReducers } from "redux";

import dontFillsReducer from "../dontFillsSlice";
import scenariosReducer from "../scenariosSlice";

export const appReducer = combineReducers({
  dontFillsState: dontFillsReducer,
  scenariosState: scenariosReducer,
});
