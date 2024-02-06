from typing import Callable, ContextManager, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.logger import logger
from metadata.core.domain.app import Organization
from metadata.core.domain.status import Status
from metadata.core.database import utils
from metadata.api.organization.internal import gcp_project_iam


class OrganizationMaintainer:
    def __init__(self, db_session: Callable[[], ContextManager[Session]], dry_run: bool):
        self.db_session = db_session
        self.dry_run = dry_run


    def process_non_success(self):
        with self.db_session() as session:
            utils.maintainer_lock(session)
            organizations: List[Organization] = session.scalars(select(Organization).where(Organization.status != Status.SUCCESS)).unique().all()
            logger.info(f"Got {len(organizations)} organizations to process")
            if organizations:
                for idx, organization in enumerate(organizations):
                    organization: Organization
                    logger.info(f"Processing organization {organization.name} [{idx + 1} / {len(organizations)}]")
                    if not self.dry_run:
                        role = f"projects/{organization.gcp_project_id}/roles/gametuner.clientAdmin"
                        gcp_project_iam.set_role_members(organization.gcp_project_id, role, [o.principal for o in organization.gcp_project_principals])
                    organization.set_status(Status.SUCCESS)
                    session.commit()
            logger.info("Processed organizations")
