import React from "react";
import { render, act, fireEvent } from "@testing-library/react";
import Board from "../src/components/Board";
import { MockChess } from "../__mocks__/MockChess";
import "@testing-library/jest-dom";

jest.mock("socket.io-client", () => {
  const onMock = jest.fn();
  const emitMock = jest.fn();
  const socketMock = { on: onMock, emit: emitMock };
  return { connect: jest.fn(() => socketMock) };
});
const changeMoveSanMock = jest.fn();

jest.mock("chess.js", () => ({
  Chess: jest.fn(() => new MockChess()),
}));

describe("Board Component", () => {
  it("renders without crashing", () => {
    render(<Board />);
  });

  it("Loading..", () => {
    const { getByTestId } = render(<Board isLoadingGame={true} />);
    const Loading = getByTestId("Loading");
    expect(Loading).toBeInTheDocument();
  });

  it("handles square click and promotion piece select", async () => {
    const { getByTestId } = render(<Board isLoadingGame={false} />);
    const chessboard = getByTestId("chessboard");
    expect(chessboard).toBeInTheDocument();
  });
});
