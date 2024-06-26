import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";


export interface DocumentDBClusterProps {
    env: pulumi.Input<string>
    vpcId: pulumi.Input<string>
    instanceClass?: pulumi.Input<string>
    multiAZ?: pulumi.Input<boolean>
    port?: pulumi.Input<number>

    backupRetentionPeriod?: pulumi.Input<number>
    backupWindow?: pulumi.Input<string>
    maintenanceWindow?: pulumi.Input<string>

    alertSnsTopicArn?: pulumi.Input<string>
}

export class DocumentDBCluster extends pulumi.ComponentResource {

    constructor (
        name: string,
        props: DocumentDBClusterProps,
        opts?: pulumi.ComponentResourceOptions,
    ) {
        super("decodingml:main:DocumentDBCluster", name, {}, opts);


        const parameterGroup = new aws.docdb.ClusterParameterGroup(`${name}-docdb-parameter-group`, {
            name: `pi-${props.env}-cluster-parameter-group`,
            description: `Parameter group configuration for pi-${props.env}-cluster`,
            family: "docdb5.0",
            parameters: [
                {
                    "name": "profiler",
                    "value": "enabled"
                },
                {
                    "name": "audit_logs",
                    "value": "disabled"
                },
                {
                    "name": "tls",
                    "value": "disabled"
                },
                {
                    "name": "ttl_monitor",
                    "value": "enabled"
                }
            ]
        }, {parent: this})

        const subnetGroup = new aws.docdb.SubnetGroup(`${name}-docdb-subnet-group`, {
            name: `pi-${props.env}-cluster-subnet-group`,
            description: `VPC subnet group for the cf-${props.env}-${name}-cluster`,
            subnetIds: pulumi.output(aws.ec2.getSubnets({tags: {Type: 'private'}})).ids,
            tags: {
                Name: `pi-${props.env}-cluster-subnet-group`
            }
        }, {parent: this})

        const securityGroup = new aws.ec2.SecurityGroup(`${name}-docdb-sg`, {
            name: `pi-${props.env}-docdb-cluster-sg`,
            description: "Database access",
            vpcId: props.vpcId,
            tags: {
                Name: `pi-${props.env}-docdb-cluster-sg`
            },
            egress: [{
                protocol: "-1",
                description: "Allow all outbound traffic by default",
                fromPort: 0,
                toPort: 0,
                cidrBlocks: ["0.0.0.0/0"],
            }],
        }, {parent: this})

        const cluster = new aws.docdb.Cluster(`${name}-docdb-cluster`, {
            // availabilityZones:  pulumi.output(aws.getAvailabilityZones({state: "available"}) if props.multiAZ else
            backupRetentionPeriod: props.backupRetentionPeriod || 7,
            clusterIdentifier: `pi-${props.env}-${name}-cluster`,
            dbClusterParameterGroupName: parameterGroup.name,
            masterUsername: pulumi.output(aws.ssm.getParameter(
                { name: `/${props.env}/${name}/cluster/master/username` })).value,
            masterPassword: pulumi.output(aws.ssm.getParameter(
                { name: `/${props.env}/${name}/cluster/master/password` })).value,
            engineVersion: "5.0.0",
            port: props.port || 27017,
            preferredBackupWindow: props.backupWindow,
            preferredMaintenanceWindow: props.maintenanceWindow,
            dbSubnetGroupName: subnetGroup.name,
            storageEncrypted: true,
            skipFinalSnapshot: true,
            vpcSecurityGroupIds: [ securityGroup.id ],
            tags: {
                Name: `pi-${props.env}-${name}-cluster`
            }
        }, {parent: this})

        const primaryInstance = new aws.docdb.ClusterInstance(`${name}-docdb-primary-instance`, {
            clusterIdentifier: cluster.clusterIdentifier,
            identifier: `pi-${props.env}-${name}-primary-instance`,
            instanceClass: props.instanceClass || "db.t3.medium",
            tags: {
                Name: `pi-${props.env}-${name}-primary-instance`
            }
        }, {parent: this})

        if (props.alertSnsTopicArn) {
            new aws.cloudwatch.MetricAlarm(`${name}-docdb-high-cpu-ma`, {
                alarmActions: [ props.alertSnsTopicArn ],
                name: `pi-${props.env}-docdb-cluster-high-cpu-alarm`,
                alarmDescription: "CPU Utilization on Database Cluster is too high",
                comparisonOperator: "GreaterThanOrEqualToThreshold",
                dimensions: {
                    DBClusterIdentifier: cluster.clusterIdentifier
                },
                evaluationPeriods: 2,
                metricName: "CPUUtilization",
                namespace: "AWS/DocDB",
                period: 300,
                statistic: "Average",
                threshold: 80,
                unit: "Percent",
            }, {parent: this})

            new aws.cloudwatch.MetricAlarm(`${name}-docdb-storage-usage-ma`, {
                alarmActions: [ props.alertSnsTopicArn ],
                name: `pi-${props.env}-docdb-cluster-storage-usage-alarm`,
                alarmDescription: "2Gb left of storage available on Database Cluster",
                comparisonOperator: "LessThanOrEqualToThreshold",
                dimensions: {
                    DBClusterIdentifier: cluster.clusterIdentifier
                },
                evaluationPeriods: 2,
                metricName: "FreeStorageSpace",
                namespace: "AWS/DocDB",
                period: 300,
                statistic: "Maximum",
                threshold: 2147483648, // 2 GB in bytes
                unit: "Bytes",
            }, {parent: this})
        }
    }
}