import argparse
import configparser
import os
import re
import subprocess
import time

import boto3

config = configparser.ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.ini")
config.read(config_path)

ecs_client = boto3.client("ecs")
ssm_client = boto3.client("ssm")


def get_running_task(client, cluster, task_definition):
    response = client.list_tasks(cluster=cluster, desiredStatus="RUNNING")
    tasks = response["taskArns"]
    if not tasks:
        return None

    described = client.describe_tasks(cluster=cluster, tasks=tasks)
    for task in described["tasks"]:
        if re.search(r"task-definition/([^:]+)", task["taskDefinitionArn"]):
            return task
    return None


def run_task(client, cfg):
    response = client.run_task(
        cluster=cfg["cluster"],
        taskDefinition=cfg["task_definition"],
        launchType=cfg.get("launch_type", "FARGATE"),
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": [cfg["subnet"]],
                "securityGroups": [cfg["security_group"]],
                "assignPublicIp": "DISABLED",
            }
        },
        enableExecuteCommand=True,
    )
    tasks = response.get("tasks", [])
    if not tasks:
        raise Exception(f"Failed to run task: {response}")
    return tasks[0]


def wait_for_execute_command_agent(client, cluster, task_arn, delay=5, max_attempts=60):
    attempts = 0

    while attempts < max_attempts:
        response = client.describe_tasks(cluster=cluster, tasks=[task_arn])
        tasks = response.get("tasks", [])
        ecs_exec_agent_status = tasks[0]["containers"][0]["managedAgents"][0][
            "lastStatus"
        ]
        if ecs_exec_agent_status == "RUNNING":
            return tasks[0]

        time.sleep(delay)
        attempts += 1

    return False


def execute_command(cfg, task_id, container_name):
    cluster = cfg["cluster"]
    cmd = [
        "aws",
        "ecs",
        "execute-command",
        "--cluster",
        cluster,
        "--task",
        task_id,
        "--container",
        container_name,
        "--interactive",
        "--command",
        "/bin/sh",
    ]

    subprocess.run(cmd)


def start_ssm_session(db_cfg, cluster, task_id, runtime_id):
    target = f"ecs:{cluster}_{task_id}_{runtime_id}"
    cmd = [
        "aws",
        "ssm",
        "start-session",
        "--target",
        target,
        "--document-name",
        "AWS-StartPortForwardingSessionToRemoteHost",
        "--parameters",
        f'{{"portNumber":["{db_cfg["remote_port"]}"],'
        f'"localPortNumber":["{db_cfg["local_port"]}"],'
        f'"host":["{db_cfg["db_host"]}"]}}',
    ]
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        "-p",
        help="プロファイル名(base, base2など)",
        default="base",
    )
    parser.add_argument(
        "--db", "-d", help="DB接続定義のセクション名(fk-test-auroraなど)"
    )

    args = parser.parse_args()
    profile = args.profile
    base_cfg = config[profile]

    task = get_running_task(
        ecs_client, base_cfg["cluster"], base_cfg["task_definition"]
    )

    if task:
        print(f"Found running task: {task['taskArn']}")
    else:
        print("No existing task found. Running new task...")
        task = run_task(ecs_client, base_cfg)
        if wait_for_execute_command_agent(
            ecs_client, base_cfg["cluster"], task["taskArn"]
        ):
            print(f"Task started: {task['taskArn']}")
        else:
            print("時間内に ECS Exec Agent が RUNNING になりませんでした。")
            exit(1)

    container = task["containers"][0]
    task_id = container["taskArn"].split("/")[-1]

    if db := args.db:
        runtime_id = container["runtimeId"]
        cluster = base_cfg["cluster"]
        db_cfg = config[f"{profile}.{db}"]
        start_ssm_session(db_cfg, cluster, task_id, runtime_id)
    else:
        container_name = container["name"]
        execute_command(base_cfg, task_id, container_name)


if __name__ == "__main__":
    main()
