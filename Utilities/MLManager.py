def get_model(model_name):
    # 1. 종목별로 매매시점 학습 한/할 모델을 가져온다
    # 2. 종목별로 매매시점 학습한 모델을 되돌려준다
    # return mdel
    pass

def PredictBuySalePoint(item):
    # 1. 종목별로 매매시점 학습 한 모델을 가져온다
    # model = get_model(model_name, item)
    # 2. 종목별로 학습한 weight를 적용한다
    # 3. 예측할 시점의 예측 데이터를 읽어 온다.
    # 4. 가져온 모델로 예측을 실행 한다.
    # model.predict()...
    # 5. 모델의 예측 결과를 돌려 준다.
    pass

def LeanBuySalePoint(item):
    ### async를 사용하여 백그라운드로 학습 하도록 한다.
    # 1. 종목별로 매매시점 학습 할 모델을 가져온다
    # 2. 학습시킬 자료를 가져온다
    # 3. 모델을 컴파일하고 학습 시킨다.
    # 4. 학습된 weight를 저장한다.
    pass


# 학습 모델을 정의한다.