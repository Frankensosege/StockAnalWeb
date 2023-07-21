class analUtility:
    def getDPCRate(self):
        #주가 일간 변동률 계산
        ret_dpc = (self.stkClose['Close'] / self.stkClose['Close'].shift(1) - 1) * 100
        ret_dpc.iloc[0] = 0

        return ret_dpc

    def getDPCCum(self, dcpRate):
        #주가 일간 변동률 누적곱
        ret_dpc_cp = ((100 + dcpRate) / 100).cumprod() * 100 - 100
        return ret_dpc_cp