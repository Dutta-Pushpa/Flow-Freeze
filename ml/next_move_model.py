"""Next-move prediction kept separate from business intervention policy."""
class NextMoveModel:
    labels=("forward","cashout","other")
    def predict_proba(self,features):
        n=len(features); return [{"forward":.12,"cashout":.81,"other":.07} for _ in range(n)]
