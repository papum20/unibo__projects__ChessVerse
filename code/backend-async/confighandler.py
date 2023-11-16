_configs = {}

def load_configs(csv_path):
    global _configs
    with open(csv_path, newline="") as csvfile:
        rows = csv.reader(csvfile, delimiter=",", quotechar='"')
        for idx, (level, row) in enumerate(rows):
            if level in configs:
                configs[level]["front" if idx % 26 >= 13 else "back"].append(row)
            else:
                configs[level] = {"front": [], "back": [row]}
    return _configs

def get_configs():
    if bool(_configs):
        return _configs
    return None

def gen_start_fen(rank=50):
    rank = max(min(int(rank), 100), 0)

    def get_ref_ranks(ref_rank):
        return [ref_rank // 10 * 10, (ref_rank // 10 + (1 if ref_rank % 10 >= 5 else 0)) * 10]

    def gen_config(ranks, row_type):
        row_configs = [
            random.choice(configs[str(ranks[i])][row_type.value]) for i in range(len(ranks))
        ]
        return row_configs[0][:5] + row_configs[1][5:]

    wb = gen_config(get_ref_ranks(rank), RowType.BACK)
    wf = gen_config(get_ref_ranks(rank), RowType.FRONT)
    bb = gen_config(get_ref_ranks(100 - rank), RowType.BACK)
    bf = gen_config(get_ref_ranks(100 - rank), RowType.FRONT)
    castle = f"""{
        'Q' if wb[0] == 'r' else ''}{
        'K' if wb[7] == 'r' else ''}{
        'q' if bb[0] == 'r' else ''}{
        'k' if bb[7] == 'r' else ''}"""
    return f"{bb}/{bf}/8/8/8/8/{wf.upper()}/{wb.upper()} w {castle if len(castle) else '-'} - 0 1"

def test_configs():
    def gen_config(ranks, row_type):
        row_configs = [
            random.choice(configs[str(ranks[j])][row_type.value]) for j in range(len(ranks))
        ]
        return row_configs[0][:5] + row_configs[1][5:]

    errs = 0
    oks = 0
    for rank in range(0, 110, 10):
        for i in range(13):
            wb = gen_config([rank], RowType.BACK)
            wf = gen_config([rank], RowType.FRONT)
            bb = gen_config([100 - rank], RowType.BACK)
            bf = gen_config([100 - rank], RowType.FRONT)
            castle = f"""{
                'Q' if wb[0] == 'r' else ''}{
                'K' if wb[7] == 'r' else ''}{
                'q' if bb[0] == 'r' else ''}{
                'k' if bb[7] == 'r' else ''}"""
            fen = f"""{bb}/{bf}/8/8/8/8/{
                wf.upper()}/{wb.upper()} w {castle if len(castle) else "-"} - 0 1"""
            try:
                chess.Board(fen)
            except Exception as e:
                print(e)
                print(fen, "    ", rank, i)
                errs += 1
            else:
                oks += 1
