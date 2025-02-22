import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  loading: false,
  result: [],
  error: null,
};

const scenariosSlice = createSlice({
  name: "scenarios",
  initialState: initialState,
  reducers: {
    setScenarios: (state, action) => {
      state.result = action.payload;
    },
    resetScenarios: (state, _action) => {
      state.result = [];
    },
  },
});

export const { setScenarios, resetScenarios } = scenariosSlice.actions;
export default scenariosSlice.reducer;
