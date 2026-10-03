"""Next-move model trained on reproducible behavioral scenarios."""
from ml.training import predict_next_move as _predict_next_move
class NextMoveModel:
    labels=("forward","cashout","other")
    def predict_proba(self, features): return [_predict_next_move(item) for item in features]
