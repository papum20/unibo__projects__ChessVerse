import Start from "/code/app/src/components/Start.jsx";
import { describe, expect, it } from "@jest/globals";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

describe("Start component works properly", () => {
  it("renders", () => {
    render(<Start />);
    expect(screen.getByTestId("startPage")).toBeInTheDocument();
  });

  it("navigates correctly to the Game component", async () => {
    render(
      <MemoryRouter initialEntries={["./game"]}>
        <Start />
      </MemoryRouter>,
    );
    expect(screen.getByTestId("game")).toBeInTheDocument();
  });
});
