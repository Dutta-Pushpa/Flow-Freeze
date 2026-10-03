from ml.training import predict_next_move as _predict_next_move

def predict_next_move(features):
    if not features: raise ValueError("behavioral features are required for next-move inference")
    return _predict_next_move(features)
