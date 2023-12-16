import Game from "/code/app/src/components/Game.jsx";
import { jest, describe, expect, it, beforeAll, afterAll } from "@jest/globals";
import { render } from "@testing-library/react";
import { io } from "socket.io-client";

jest.mock("socket.io-client", () => {
  const onMock = jest.fn();
  const emitMock = jest.fn();
  const socketMock = { on: onMock, emit: emitMock };
  return { connect: jest.fn(() => socketMock) };
});

describe("Game component", () => {
  it("renders without crashing", () => {
    render(<Game />);
  });

  it("shows game over modal", (done) => {});

  it("shows victory modal", () => {});

  it("shows menu modal", () => {});
});
