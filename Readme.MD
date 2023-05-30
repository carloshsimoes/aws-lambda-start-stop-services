# Lambda para Ligar/Desligar Instâncias RDS e Services (ECS)

Lambda para desligar/ligar instâncias RDS e Services (ECS) em horários determinados, se apoiando em Triggers/CRON (Eventbridge).

Em ambientes de DEV/HOMOLOG e outros, muitas vezes temos cargas de services (ECS Cluster) em execução assim como instâncias do Amazon RDS, em horários que não são utilizados. Logo, a proposta é poder deixar agendado os horários em que esses workloads deverão estar disponíveis (online), podendo reduzir a carga total de horas UP, reduzindo assim os custos.

Da forma como foi configurada a Lambda, na mesma Lambda poderá executar os fluxos de Start/Stop do(s) recurso(s), não sendo necessário criar uma Lambda para ligar e outra Lambda para Desligar.


&nbsp;

# Para configurar a Lambda, informar as especificações do Runtime:

## Runtime Settings

- NomeScript: lambda.py

- Runtime: Python 3.7

- Handler: lambda.handler

&nbsp;


# Permissions / Execution Role:

Uma vez que a Lambda precisa ter permissão para performar as ações específicas nos recursos, adicionar em sua ROLE a policy, como exemplo:

```

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecs:ListContainerInstances",
                "ecs:ListServices"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecs:StartTask",
                "ecs:StopTask",
                "ecs:UpdateService"
            ],
            "Resource": [
                "arn:aws:ecs:{AWS_REGION}:{ACCOUNT_ID}:service/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "rds:StartDBCluster",
                "rds:StartDBInstance",
                "rds:StopDBCluster",
                "rds:StopDBInstance",
                "rds:DescribeDBInstances"
            ],
            "Resource": [
                "arn:aws:rds:{AWS_REGION}:{ACCOUNT_ID}:db:*"
            ]
        }
    ]
}


```

&nbsp;


## Triggers:

Será necessário somente criar 2 Triggers, EventBridge (CloudWatch Events), com os agendamentos CRON desejados (ex: Ligar, Desligar).

Na criação do Event, além da expressão CRON em Event Schedule, em Target especificar o `input constant`, o objeto/JSON correspondente.

**No objeto/JSON, deverão ser definidos:**

> **action**: start | stop

**Resources**; Uma lista com os recursos (RDS ou ECS), no qual iremos informar:

> **service**: ecs | rds
> **identifier**: ARN do Cluster ECS ou Nome da Instância RDS;
> **region**: Região do recurso, ex: us-east-1


- Exemplo: Start ECS Services and RDS Instance:

```json

{
  "action": "start",
  "resources": [
      {
          "service": "ecs",
          "identifier": "arn:aws:ecs:us-east-1:{ACCOUNT_ID}:cluster/dev",
          "region": "us-east-1"
      },
      {
          "service": "rds",
          "identifier": "dev-database",
          "region": "us-east-1"
      },
  ]
}


```


- Exemplo: Stop ECS Services and RDS Instance:

```json

{
  "action": "stop",
  "resources": [
      {
          "service": "ecs",
          "identifier": "arn:aws:ecs:us-east-1:{ACCOUNT_ID}:cluster/dev",
          "region": "us-east-1"
      },
      {
          "service": "rds",
          "identifier": "dev-database",
          "region": "us-east-1"
      },
  ]
}


```
