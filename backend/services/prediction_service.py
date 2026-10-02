from ml.next_move_model import NextMoveModel
def predict_next_move(features=None): return NextMoveModel().predict_proba([features or {}])[0]
