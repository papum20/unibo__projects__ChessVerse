import React from "react";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import App from "../src/App";

/*
  Non si può testare? 
*/
import "@testing-library/jest-dom";
test("renders App component", () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>,
  );
  expect(screen.getByTestId("appPage")).toBeInTheDocument();
});
