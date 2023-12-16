import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom"; // Importa MemoryRouter
import NoRoute from "../src/NoRoute";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

test("No Route renders successfully", async () => {
  render(
    <MemoryRouter>
      <NoRoute />
    </MemoryRouter>,
  );
  const spanElement = screen.getByTestId("textComponent");
  expect(spanElement).toHaveTextContent("torna alla pagina di");

  const button = screen.getByTestId("goBack");
  expect(button).toHaveTextContent("start");

  fireEvent.click(button);

  await waitFor(() => {
    expect(window.location.pathname).toBe("/");
  });
});
