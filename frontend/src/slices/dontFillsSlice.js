import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  loading: false,
  result: [],
  error: null,
};

const dontFillsSlice = createSlice({
  name: "dontFills",
  initialState: initialState,
  reducers: {
    handleDontFillAdd: (state, action) => {
      state.result.push(action.payload);
    },
    handleDontFillDelete: (state, action) => {
      state.result = state.result.filter(
        (df) => df.startDate !== action.payload.startDate
      );
    },
    handleChangeDontFillColor: (state, action) => {
      state.result = state.result.map((df) =>
        df.startDate === action.payload.startDate
          ? { ...df, color: action.payload.color }
          : df
      );
    },
    handleChangeDontFillDescription: (state, action) => {
      state.result = state.result.map((df) =>
        df.startDate === action.payload.startDate
          ? { ...df, description: action.payload.description }
          : df
      );
    },
    resetDontFills: (state, _action) => {
      state.result = [];
    },
  },
});

export const {
  handleChangeDontFillColor,
  handleChangeDontFillDescription,
  handleDontFillAdd,
  handleDontFillDelete,
  resetDontFills
} = dontFillsSlice.actions;
export default dontFillsSlice.reducer;
