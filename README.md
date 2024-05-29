# CDK Guardrails for Application Development

## Background

The AWS Cloud Development Kit (AWS CDK) is an open-source software development framework to define cloud infrastructure in code and provision it through AWS CloudFormation. It enables developers to compose and share cloud application resources in familiar programming languages such as TypeScript, Python, Java etc. By abstracting away the complexity of manually writing CloudFormation templates, the AWS CDK accelerates the development process, allowing developers to build cloud applications quickly and with greater ease.

The AWS CDK provides high-level components called constructs, which pre-configure cloud resources with sensible defaults, making it easier to set up complex environments. Developers can also create custom constructs to encapsulate and reuse cloud patterns specific to their applications. This approach not only speeds up the development cycle but also ensures consistency and best practices across deployments. The AWS CDK integrates seamlessly with other AWS services and tools, further enhancing the developer experience and productivity on the AWS platform. 

With that said, one of the big challenges of AWS CDK adoption is the bootstrap. The bootstrap is itself a generated, versioned Cloudformation template that provisions resources that are required by the CDK to deploy applications into each AWS account and region. It includes an S3 bucket for storing assets and IAM roles that the CDK assumes to stage templates, artifacts, perform lookups and deploy resources.

Out of the box, the bootstrap includes two roles for deployment activities:

* `cdk-<qualifier>-deploy-role-<account>-<region>`: This role is assumed by the CDK command to initiate deployment (e.g. `cloudformation:CreateStack`)
* `cdk-<qualifier>-cfn-exec-role-<account>-<region>`: This role is passed by the CDK command to the Cloudformation service and is the role that is used to deploy AWS resources

Per default, the `AdministratorAccess` policy is attached to the `cfn-exec` role. The outcome is that there are no restrictions to what the role can deploy. This is often a problem in organisations where a least privilege mindset and permissions are required. In addition, AWS accounts typically contain landing zone components and stacks that must be protected from change by application stacks. The good news is that the CDK bootstrap can be customised to meet such requirements and guardrails.

However, creating a bootstrap for each application is unfeasible and therefore a middle-ground must be struck, which meets security requirements and guardrails while also enabling developers to develop relatively unhindered.

At [Virtuability](https://www.virtuability.com) we have helped organisations to adopt a tiered approach to bootstraps that are secure and help protect landing zone components. This has helped developers develop while also meeting said security requirements and guardrails.

This repository demonstrates a sample customised CDK bootstrap that implements common guardrails. The sample bootstrap is geared towards MLOps workloads such as Sagemaker related deployments but can be customised for many other purposes.

## Guardrails

The following rules apply to the CDK bootstrap:

1. The CDK can create roles but must attach a suitable [permissions boundary](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html)
2. Policies, roles and instance profiles must be namespaced (/apppolicies/, /approles/, /appinstanceprofiles/). This prevents changes to IAM resources outside of these namespaces and therefore protects the landing zone
3. Permissions boundaries can be split up by "job function" or a purpose. In this sample we create three permissions boundaries for a) app workload roles, b) custom resources and c) init resources (such as the EKS Cluster's nested template). Aspects apply the correct permissions boundary based on a given construct's context
4. Whitelist allowed AWS services only. Also do not allow creation of a VPC or Transit Gateway but do allow creation of EC2 instances
5. Optionally include particular role ARNs that can use the CDK bootstrap roles

In addition, consider that a tiered approach to multiple co-existing CDK bootstraps is possible with different qualifiers. For instance, consider that a CloudOps and System administrator team can use a bootstrap for landing zone concerns (e.g. qualifier `lz`). While app development teams use a bootstrap with qualifier `app` (or `mlops` as in this sample).

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

Instead, [Aspects](https://docs.aws.amazon.com/cdk/v2/guide/aspects.html) (visitor pattern) can be used to decorate roles with permissions boundaries that include account, region and bootstrap qualifier context. his approach will allow for multiple permissions boundaries for different purposes rather than just one.

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

## References

1. [When and where to use IAM permissions boundaries](https://aws.amazon.com/blogs/security/when-and-where-to-use-iam-permissions-boundaries/)
2. [aws-samples/example-permissions-boundary](https://github.com/aws-samples/example-permissions-boundary)
3. [How to use the PassRole permission with IAM roles](https://aws.amazon.com/blogs/security/how-to-use-the-passrole-permission-with-iam-roles/)
4. [AWS re:Inforce - Best practices for delegating access on AWS](https://d1.awsstatic.com/events/aws-reinforce-2022/IAM331_Best-practices-for-delegating-access-on-AWS.pdf)
