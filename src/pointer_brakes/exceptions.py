class DeltaPositionInvalidError(BaseException):
    def __init__(self, last=None, curr=None):
        if last and curr:
            message = f"Could not calculate delta position.  Touch positions are p1={last}, p2={curr}"
        else:
            message = "Could not calculate delta postiion.  Reached unexpected state"

        super().__init__(message)


class DeltaTimeInvalidError(BaseException):
    def __init__(self, last, curr):
        super().__init__(f"Could not calculate delta time.  Timestamps are t1={last}, t2={curr}")


class VelocityInvalidError(BaseException):
    def __init__(self):
        super().__init__("Could not calculate velocity.  Reached unexpected state")
