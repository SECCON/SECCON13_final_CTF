import math
from typing import Any, Dict, List, Optional


def distribute_score(config: Dict[str, Any], scores: List[float], bigger_is_better: Optional[bool]=True):
    """スコアをベースに点数を分配する

    Args:
      config (Dict[str, Any]): ゲームの設定情報。
      scores (List[float]): 9チームのスコア。
      bigger_is_better (bool, optional): Trueならスコアが大きいほど高い順位を与える。デフォルトはFalse。

    Returns:
      List[int]: 分配された点数のリスト。 `i` 番目の点数は引数 `score` の `i` 番目のスコアを獲得したチームに対応する。
    """
    RANK_SCORE = config['game']['scoring']
    assert len(scores) == len(RANK_SCORE), "Invalid number of teams"

    indexed_scores = [(i, sc) for i, sc in enumerate(scores)]
    indexed_scores.sort(key=lambda x: x[1], reverse=bigger_is_better)

    result = [0] * len(scores)

    prev_score = None
    prev_rank = 0
    count_processed = 0

    for idx, sc in indexed_scores:
        count_processed += 1

        if prev_score is None or \
           (bigger_is_better and sc < prev_score) or (not bigger_is_better and sc > prev_score):
            current_rank = count_processed
        else:
            current_rank = prev_rank

        point = RANK_SCORE[current_rank-1]
        result[idx] = point

        prev_score = sc
        prev_rank = current_rank

    return result


def old_distribute_score(config: Dict[str, Any], scores: List[float], bigger_is_better: Optional[bool]=True):
    """スコアをベースに点数を分配する【古い実装】

    Args:
      config (Dict[str, Any]): ゲームの設定情報。
      scores (List[float]): 9チームのスコア。
      bigger_is_better (bool, optional): Trueならスコアが大きいほど高い順位を与える。デフォルトはFalse。

    Returns:
      List[int]: 分配された点数のリスト。 `i` 番目の点数は引数 `score` の `i` 番目のスコアを獲得したチームに対応する。
    """
    assert False, "DO NOT USE THIS"

    RANK_SCORE = config['game']['scoring']
    assert len(scores) == len(RANK_SCORE), "Invalid number of teams"

    indexed_scores = list(enumerate(scores))
    indexed_scores.sort(key=lambda x: x[1], reverse=bigger_is_better)

    result = [0 for _ in range(len(scores))]
    current_rank = 1

    i, n = 0, len(scores)
    while i < n:
        tie_score = indexed_scores[i][1]
        tie_indices = [indexed_scores[i][0]]

        j = i + 1
        while j < n and indexed_scores[j][1] == tie_score:
            tie_indices.append(indexed_scores[j][0])
            j += 1

        tie_size = len(tie_indices)

        total_points = 0
        for r in range(current_rank, current_rank + tie_size):
            total_points += RANK_SCORE[r-1]

        shared_point = math.ceil(total_points / tie_size)

        for idx in tie_indices:
            result[idx] = shared_point

        i = j
        current_rank += tie_size

    return result

if __name__ == '__main__':
    from util import *
    config = load_config("../config.yml")

    score = [999.999 for _ in range(9)]
    score[1] = 3.14
    score[3] = 2.17
    score[5] = 9.99
    points = distribute_score(config, score, bigger_is_better=False)

    print(points)
    print(sum(points))
