from ml.training import predict_next_move as _predict_next_move

def predict_next_move(features=None):
    return _predict_next_move(features or {"amount":15000,"sender_velocity":5,"receiver_velocity":4,"hop_count":2,"cashout_flag":1,"new_relationship":1,"account_age_days":19,"channel":"app","merchant_flag":0})
