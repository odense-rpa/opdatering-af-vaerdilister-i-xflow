import asyncio
import logging
import sys

from automation_server_client import AutomationServer, Workqueue, WorkItemError, Credential
from kmd_nexus_client import NexusClient, OrganizationsClient
from odk_tools.tracking import Tracker
from xflow_client import XFlowClient, ValueListClient

nexusklient: NexusClient = None
nexus_organisationer: OrganizationsClient = None
afregningsklient: Tracker = None
xflowklient: XFlowClient = None
værdilisteklient: ValueListClient = None
procesnavn = "Opdatering af værdilister i Xflow"



async def populate_queue(workqueue: Workqueue):
    logger = logging.getLogger(__name__)

    logger.info("Hello from populate workqueue!")


async def process_workqueue(workqueue: Workqueue):
    logger = logging.getLogger(__name__)

    logger.info("Hello from process workqueue!")

    for item in workqueue:
        with item:
            data = item.get_data_as_dict()

            try:
                # Process the item here
                pass
            except WorkItemError as e:
                # A WorkItemError represents a soft error that indicates the item should be passed to manual processing or a business logic fault
                logger.error(f"Error processing item: {data}. Error: {e}")
                item.fail(str(e))


if __name__ == "__main__":
    ats = AutomationServer.from_environment()

    workqueue = ats.workqueue()

    # Initialize external systems for automation here..
    Nexuscredentials = Credential.get_credential("KMD Nexus - produktion")
    Afregningscredentials = Credential.get_credential("Odense SQL Server")
    XFlowcredentials_test = Credential.get_credential("Xflow - test")
    

    nexusklient = NexusClient(
        client_id=Nexuscredentials.username,
        client_secret=Nexuscredentials.password,
        instance=Nexuscredentials.data["instance"]
    )

    nexus_organisationer = OrganizationsClient(nexus_client=nexusklient)

    afregningsklient = Tracker(
        username=Afregningscredentials.username,
        password=Afregningscredentials.password,
    )

    xflowklient = XFlowClient(
        instance=XFlowcredentials_test.data["instance"],
        token=XFlowcredentials_test.password
    )

    # Queue management
    if "--queue" in sys.argv:
        workqueue.clear_workqueue("new")
        asyncio.run(populate_queue(workqueue))
        exit(0)

    # Process workqueue
    asyncio.run(process_workqueue(workqueue))
