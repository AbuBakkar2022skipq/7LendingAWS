import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda as lambdaa,
    aws_events as events_, #For Events
    aws_events_targets as target_, #For Creating Events, Generating Target Function
)
from constructs import Construct

class appStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        mylambdafun= self.createlambda("SevenLending_Data_retrieval_script","lambda_function.lambda_handler","./resources")


        #schedule=events_.Schedule.cron(day="*", hour="8")
        target =target_.LambdaFunction(handler=mylambdafun)


    def createlambda(self,id_, handler, path):
        return lambdaa.Function(self, id_, runtime=lambdaa.Runtime.PYTHON_3_7, handler=handler, code=lambdaa.Code.from_asset(path))