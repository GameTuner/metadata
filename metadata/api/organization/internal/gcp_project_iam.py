# Copyright (c) 2024 AlgebraAI All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
