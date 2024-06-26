import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";
import {DocumentDBCluster} from "./components/docdb";

const stackName = pulumi.getStack();
const accountId = pulumi.output(aws.getCallerIdentity()).accountId;
const region = pulumi.output(aws.getRegion()).name;

const databaseUriArn = pulumi.output(aws.ssm.getParameter({
    name: `/${stackName}/database/uri`
})).value

const openApiKeyArn = pulumi.output(aws.ssm.getParameter({
    name: `/${stackName}/openai/api-key`
})).value

const proxyHost = pulumi.output(aws.ssm.getParameter({
    name: `/${stackName}/proxy/host`
})).value

const proxyPort = pulumi.output(aws.ssm.getParameter({
    name: `/${stackName}/proxy/port`
})).value

const proxyUsername = pulumi.output(aws.ssm.getParameter({
    name: `/${stackName}/proxy/username`
})).value

const proxyPassword = pulumi.output(aws.ssm.getParameter({
    name: `/${stackName}/proxy/password`
})).value

const docdb = new DocumentDBCluster("reports", {
    env: stackName,
    vpcId: vpc.id,
    instanceClass: "db.t3.medium",
}, {dependsOn: vpc})

const lambdaExecutionRole = new aws.iam.Role("lambda-role", {
    assumeRolePolicy: JSON.stringify({
        Version: "2012-10-17",
        Statement: [{
            Effect: "Allow",
            Principal: {
                Service: "lambda.amazonaws.com",
            },
            Action: "sts:AssumeRole",
        }],
    }),
    inlinePolicies: [{
        name: "invoke-lambda",
        policy: JSON.stringify({
            Statement: [{
                Action: [
                    "lambda:InvokeAsync",
                    "lambda:InvokeFunction",
                    "logs:FilterLogEvents",
                ],
                Effect: 'Allow',
                Resource: '*'
            }],
            Version: '2012-10-17',
        } as aws.iam.PolicyDocument)
    }],
    managedPolicyArns: [
        aws.iam.ManagedPolicy.AmazonS3FullAccess,
        aws.iam.ManagedPolicy.AmazonDocDBFullAccess,
        aws.iam.ManagedPolicy.AWSLambdaBasicExecutionRole,
        aws.iam.ManagedPolicy.AWSLambdaVPCAccessExecutionRole,
        aws.iam.ManagedPolicy.CloudWatchLambdaInsightsExecutionRolePolicy
    ]
})

const crawlerSecurityGroup = new aws.ec2.SecurityGroup("crawler-security-group", {
    name: `pi-${stackName}-news-sg`,
    description: "Marketing reports news functions access",
    vpcId: pulumi.output(aws.ec2.getVpc({tags: {Name: `pi-${stackName}-vpc`}})).id,
    egress: [{
        protocol: "-1",
        description: "Allow all outbound traffic by default",
        fromPort: 0,
        toPort: 0,
        cidrBlocks: ["0.0.0.0/0"],
    }],
    tags: {
        Name: `pi-${stackName}-news-sg`
    }
})

const crawler = new aws.lambda.Function("crawler-function", {
    name: `pi-${stackName}-crawler`,
    imageUri: pulumi.interpolate`${accountId}.dkr.ecr.${region}.amazonaws.com/news:latest`,
    packageType: 'Image',
    description: 'Crawler lambda function',
    timeout: 300,
    memorySize: 3008,
    environment: {
        variables: {
            DATABASE_URI: databaseUriArn,
            OPENAI_API_KEY: openApiKeyArn,
            PROXY_HOST: proxyHost,
            PROXY_PORT: proxyPort,
            PROXY_USERNAME: proxyUsername,
            PROXY_PASSWORD: proxyPassword,
        }
    },
    imageConfig: {
      commands: ["src.crawler.lambda_handler"]
    },
    role: lambdaExecutionRole.arn,
    vpcConfig: {
        subnetIds: subnets,
        securityGroupIds: [crawlerSecurityGroup.id],
    }
}, {dependsOn: lambdaExecutionRole})

const scheduler = new aws.lambda.Function("scheduler-function", {
    name: `pi-${stackName}-scheduler`,
    imageUri: pulumi.interpolate`${accountId}.dkr.ecr.${region}.amazonaws.com/news:latest`,
    packageType: 'Image',
    description: 'Scheduler lambda function',
    timeout: 900,
    memorySize: 3008,
    environment: {
        variables: {
            DATABASE_URI: databaseUriArn,
            OPENAI_API_KEY: openApiKeyArn,
            PROXY_HOST: proxyHost,
            PROXY_PORT: proxyPort,
            PROXY_USERNAME: proxyUsername,
            PROXY_PASSWORD: proxyPassword,
        }
    },
    imageConfig: {
      commands: ["src.scheduler.lambda_handler"]
    },
    role: lambdaExecutionRole.arn,
    vpcConfig: {
        subnetIds: subnets,
        securityGroupIds: [crawlerSecurityGroup.id],
    }
}, {dependsOn: crawler})

export const schedulerFunctionArn = scheduler.arn
export const crawlerFunctionArn = crawler.arn