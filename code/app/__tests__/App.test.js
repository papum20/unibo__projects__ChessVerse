import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes } from "react-router-dom";
import App from "../src/App";
import "@testing-library/jest-dom";

describe("App component", () => {
  it("renders without crashing", () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByTestId("appPage")).toBeInTheDocument();
  });

  it("renders the Start component on the home route", async () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByTestId("startPage")).toBeInTheDocument();
  });

  function generateRandomString(length) {
    let result = "";
    const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    const charactersLength = characters.length;

    for (let i = 0; i < length; i++) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }

    return result;
  }

  const reservedRoutes = ["signin", "login", "game"];

  function getRandomUniqueRoute() {
    let randomRoute;
    do {
      let randomNumber = Math.floor(Math.random() * 10) + 1;
      randomRoute = generateRandomString(randomNumber);
    } while (reservedRoutes.includes(randomRoute));

    return randomRoute;
  }

  const randomUniqueRoute = getRandomUniqueRoute();

  it("navigates to NoRoute component on an invalid route", async () => {
    const randomUniqueInvalidRoute = getRandomUniqueRoute();
    render(
      <MemoryRouter initialEntries={[`/${randomUniqueInvalidRoute}`]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByTestId("noRoutePage")).toBeInTheDocument();
  });
  /* La route 'Game' va testata in 'Start' */
});
