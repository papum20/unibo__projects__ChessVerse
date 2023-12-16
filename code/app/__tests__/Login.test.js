import Login from "/code/app/src/components/Login.jsx";
import { test, expect } from "@jest/globals";
import { render, screen, waitFor } from "@testing-library/react";

test("Login renders successfully", async () => {
  render(<Login />);

  const spanElement = screen.getByTestId("loginSpan");
  expect(spanElement).toHaveTextContent("torna alla pagina di ");

  const buttonElement = screen.getByTestId("loginButton");
  expect(buttonElement).toHaveTextContent("start");

  /*
  await waitFor(() => {
    expect(window.location.pathname).toMatch();
  })
  */
});
