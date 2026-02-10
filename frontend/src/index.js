import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import App from "./App";
import * as serviceWorker from "./serviceWorker";
import { configureStore } from "@reduxjs/toolkit";
import { appReducer } from "./slices/reducers/appReducers";
import { Provider } from "react-redux";
import { ThemeProvider } from "./contexts/ThemeContext";

const store = configureStore({
  reducer: appReducer,
});

ReactDOM.render(
  <Provider store={store}>
    <ThemeProvider>
      <React.StrictMode>
        <App />
      </React.StrictMode>
    </ThemeProvider>
  </Provider>,
  document.getElementById("root") // Correct rendering for React 16
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
