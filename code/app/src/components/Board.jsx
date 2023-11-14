function Board() {
    const config = {
        draggable: true,
        position: 'start',
    };

    const board = Chessboard('board', config);

    return (
        <div id="board" style={{ width: 400 }} />
    )
}
export default Board;