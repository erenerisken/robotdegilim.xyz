import React from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";
import { configureStore } from "@reduxjs/toolkit";
import { appReducer } from "./slices/reducers/appReducers";
import { Provider } from "react-redux";
import { ThemeProvider } from "./contexts/ThemeContext";

const store = configureStore({
  reducer: appReducer,
});

createRoot(document.getElementById("root")).render(
  <Provider store={store}>
    <ThemeProvider>
      <React.StrictMode>
        <App />
      </React.StrictMode>
    </ThemeProvider>
  </Provider>
);
