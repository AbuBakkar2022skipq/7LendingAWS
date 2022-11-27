from stack.stack import appStack
import aws_cdk as cdk

app = cdk.App()

appStack(app, "appStackk", env=cdk.Environment(account="412740716366", region="us-east-2"))

app.synth()