import React from "react";
import { createRoot } from "react-dom/client";
import { StyledEngineProvider } from "@mui/material/styles";
import "./index.css";
import App from "./App";
import { configureStore } from "@reduxjs/toolkit";
import { appReducer } from "./slices/reducers/appReducers";
import { Provider } from "react-redux";
import { ThemeProvider } from "./contexts/ThemeContext";

const store = configureStore({
  reducer: appReducer,
});

// injectFirst puts MUI's own styles ahead of ours in the document, so the
// app's stylesheets and withStyles rules win on equal specificity instead of
// needing !important to be heard.
createRoot(document.getElementById("root")).render(
  <Provider store={store}>
    <ThemeProvider>
      <React.StrictMode>
        <StyledEngineProvider injectFirst>
          <App />
        </StyledEngineProvider>
      </React.StrictMode>
    </ThemeProvider>
  </Provider>
);
