class MockChess {
  constructor() {
    this.moves = jest.fn(() => []);
    this.move = jest.fn(() => ({ san: "mock-move" }));
    this.fen = jest.fn(() => "mock-fen");
    this.load = jest.fn();
    this.undo = jest.fn();
  }
}

export { MockChess };
