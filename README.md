# CDK Guardrails for Application Development

## Architecture

The following diagram provides an overview of how to enable developers to develop and deploy workloads that must adhere to certain guardrails.

![CDK Guardrails overview](./diagrams/General%20iam%20cdk%20cfn%20development%20guardrails.drawio.png)

### A note on permissions boundaries

While it's technically possible to set the permissions boundary out-of-the-box - per below - via the `cdk.json` file with the following `context` this is not as flexible as using an Aspect visitor pattern.

```json
    "@aws-cdk/core:permissionsBoundary": {
      "name": "cdk-mlops-permissions-boundary-123456789012-eu-west-1"
    },
```

Setting the Permissions Boundary like this will prevent multi-account and multi-region CDK apps from deploying successfully.

There are various workarounds, such as only deploying the Permissions Boundary in a single region per account by Cloudformation condition while dropping region and account id from the name. But, at best, that's a workaround.

In addition, using the above mechanism will not add Permissions Boundaries to roles during unit tests and they can therefore not be tested. 

Instead, [Aspects](https://docs.aws.amazon.com/cdk/v2/guide/aspects.html) (visitor pattern) can be used to decorate roles with the permissions boundary with account, region and bootstrap qualifier context.

## CDK Bootstrap Deployment

The following sections detail how to either deploy the CDK bootstrap in a single account & region.

The input parameters to the stack do not fundamentally differ from the [standard bootstrap](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html#bootstrapping-customizing) with one exception:

*  When deploying via the bootstrap from one account to another (e.g from a Shared Services account), the standard bootstrap does not offer an option to be more granular in the trust relationship between the accounts beyond account id. This customised bootstrap offers the `TrustedAccountsRoles` input parameter, which is a comma-separated list of role ARNs (or role ARN patterns with wildcard `*`) to further narrow what roles can deploy from the trusted account to the deployment account.

### Deploy to a single account/region

The following AWS CLI command provides an example on how to deploy the CDK bootstrap to a single account & region with the following notes:

* Use an AWS managed S3 encryption key
* The boostrap trusts another account (`123456789012`) from where deployments can be made to the account in which the bootstrap exists
* Enables the Developer & SystemAdmin AWS SSO permission sets (roles) to make deployments from the trusted account to the deployment account
* Qualifier on the CDK bootstrap is "mlops" (note that CDK apps must have the [bootstrap qualifier set accordingly](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html#bootstrapping-custom-synth) to use the bootstrap)
* Set the `BootstrapVariant` to be anything other than the default value in order to avoid accidental to avoid an accidental bootstrap overwrite

```bash
# Create CDK bootstrap stack
aws cloudformation create-stack \
 --stack-name CDKBootstrapMLOps \
 --template-body file://bootstrap/bootstrap.yaml \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameters ParameterKey=Qualifier,ParameterValue=mlops \
   ParameterKey=FileAssetsBucketKmsKeyId,ParameterValue=AWS_MANAGED_KEY \
   ParameterKey=BootstrapVariant,ParameterValue=mlops \
   ParameterKey=TrustedAccounts,ParameterValue=123456789012 \
   ParameterKey=TrustedAccountsRoles,ParameterValue='"arn:aws:iam::123456789012:role/aws-reserved/sso.amazonaws.com/eu-west-1/AWSReservedSSO_Developer_*,arn:aws:iam::123456789012:role/aws-reserved/sso.amazonaws.com/eu-west-1/AWSReservedSSO_SystemAdmin_*"'

# Update CDK bootstrap stack
aws cloudformation update-stack \
 --stack-name CDKBootstrapMLOps \
 --template-body file://bootstrap/bootstrap.yaml \
 --capabilities CAPABILITY_NAMED_IAM \
 --parameters ParameterKey=Qualifier,ParameterValue=mlops \
   ParameterKey=FileAssetsBucketKmsKeyId,ParameterValue=AWS_MANAGED_KEY \
   ParameterKey=BootstrapVariant,ParameterValue=mlops \
   ParameterKey=TrustedAccounts,ParameterValue=123456789012 \
   ParameterKey=TrustedAccountsRoles,ParameterValue='"arn:aws:iam::123456789012:role/aws-reserved/sso.amazonaws.com/eu-west-1/AWSReservedSSO_Developer_*,arn:aws:iam::123456789012:role/aws-reserved/sso.amazonaws.com/eu-west-1/AWSReservedSSO_SystemAdmin_*"'
```


## Sample CDK app

In the `samples/cdk-app` directory there is a sample CDK app that demonstrates all aspects of using the CDK bootstrap with guardrails.

This includes:
* An aspect that adds the CDK bootstrap permissions boundary to all roles defined in the CDK app (see `samples/cdk-app/common/iam_pb_aspect.py`)
* An aspect that automatically adds a path to every IAM policy, role and instance profile (see `samples/cdk-app/common/iam_path_aspect.py`)

## TODO

* Add explicit support for custom resource roles and policies in a separate sub-namespace (e.g. `/approles/cr/`)
