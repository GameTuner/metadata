from typing import List
from fastapi.logger import logger
from google.cloud import resourcemanager_v3
from google.iam.v1 import iam_policy_pb2
from google.iam.v1.policy_pb2 import Policy, Binding

def set_role_members(project_id: str, role_id: str, members: List[str]):
    client = resourcemanager_v3.ProjectsClient()
    policy: Policy = client.get_iam_policy(iam_policy_pb2.GetIamPolicyRequest(
        resource=f'projects/{project_id}'
    ))
    role_bindings = [b for b in policy.bindings if b.role == role_id]
    logger.info(f"Role role bindings for {project_id} before change: {policy.bindings}")
    if role_bindings:
        del role_bindings[0].members[:]
        role_bindings[0].members.extend(members)
    else:
        policy.bindings.append(Binding(
            role=role_id,
            members=members
        ))
    client.set_iam_policy(iam_policy_pb2.SetIamPolicyRequest(
        resource=f'projects/{project_id}',
        policy=policy,
    ))
    logger.info(f"Role role bindings for {project_id} after change: {policy.bindings}")
