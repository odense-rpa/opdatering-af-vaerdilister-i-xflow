import asyncio
import logging
import sys

from automation_server_client import AutomationServer, Workqueue, WorkItemError, Credential
from kmd_nexus_client import NexusClient, OrganisationerClient
from odk_tools.tracking import Tracker
from xflow_client import XFlowClient, ValueListClient

nexusklient: NexusClient = None
nexus_organisationer: OrganisationerClient = None
afregningsklient: Tracker = None
xflowklient: XFlowClient = None
værdilisteklient: ValueListClient = None
procesnavn = "Opdatering af værdilister i Xflow"

# Bruger alle organisationer i Nexus til at opdatere værdilisten i XFlow
async def opdater_organisationer_i_XFlow():
    logger = logging.getLogger(__name__)
    logger.info("Opdaterer organisationer i Nexus")

    # Finder værdiliste samt UUID for værdilisten
    værdiliste = værdilisteklient.search_value_lists("Nexus - organisationer")
    værdiliste_uuid = værdiliste[0]["id"] if værdiliste else None
    if værdiliste_uuid is None:
        logger.error("Værdiliste 'Nexus - organisationer' blev ikke fundet.")
        return

    # Henter organisationer fra Nexus
    alle_organisationer = nexus_organisationer.hent_organisationer()
    
    # Laver listen om til det format, der kræves af Xflow
    organisationer = [{"value": x["name"], "key": str(i + 1), "oprettetAf": "RPA"} for i, x in enumerate(alle_organisationer)]
    try:
        værdilisteklient.update_value_list(
            værdiliste_uuid,
            organisationer,
        )
    except Exception as e:
        logger.error(f"Failed to update value list: {e}")

# Bruger alle leverandører i Nexus til at opdatere værdilisten i XFlow
async def opdater_leverandører_i_XFlow():
    logger = logging.getLogger(__name__)
    logger.info("Opdaterer leverandører i XFlow")

    # Finder værdiliste samt UUID for værdilisten
    værdiliste = værdilisteklient.search_value_lists("Nexus - leverandører")
    værdiliste_uuid = værdiliste[0]["id"] if værdiliste else None
    if værdiliste_uuid is None:
        logger.error("Værdiliste 'Nexus - leverandører' blev ikke fundet.")
        return

    # Henter leverandører fra Nexus
    alle_leverandører = nexus_organisationer.hent_leverandører()

    # Laver listen om til det format, der kræves af Xflow
    leverandører = [{"value": x["name"], "key": str(i + 1), "oprettetAf": "RPA"} for i, x in enumerate(alle_leverandører)]
    try:
        værdilisteklient.update_value_list(
            værdiliste_uuid,
            leverandører,
        )
    except Exception as e:
        logger.error(f"Failed to update value list: {e}")
    
# Bruger kun organisationsleverandører i Nexus til at opdatere værdilisten i XFlow
async def opdater_organisationsleverandører_i_XFlow():
    logger = logging.getLogger(__name__)
    logger.info("Opdaterer organisationsleverandører i XFlow")
    godkendte_paragraffer = ["§ 7 Ældreloven","§ 9 Ældreloven","§ 9 stk. 2 Ældreloven","§ 11 Ældreloven","§ 16 Ældreloven"]

    # Finder værdiliste samt UUID for værdilisten
    værdiliste = værdilisteklient.search_value_lists("Nexus - organisationsleverandører")
    værdiliste_uuid = værdiliste[0]["id"] if værdiliste else None
    if værdiliste_uuid is None:
        logger.error("Værdiliste 'Nexus - organisationsleverandører' blev ikke fundet.")
        return

    # Henter leverandører fra Nexus
    alle_leverandører = nexus_organisationer.hent_leverandører()

    # fjern alle leverandører hvor typen ikke er "organization", og hvor der minimum et af felterne i "paragraph" der matcher en af de godkendte paragraffer
    alle_leverandører = [x for x in alle_leverandører 
                    if x["type"] == "organization" and 
                    any(paragraf in x.get("paragraph", "") for paragraf in godkendte_paragraffer)]

    # Laver listen om til det format, der kræves af Xflow
    leverandører = [{"value": x["name"], "key": str(i + 1), "oprettetAf": "RPA"} for i, x in enumerate(alle_leverandører)]
    try:
        værdilisteklient.update_value_list(
            værdiliste_uuid,
            leverandører,
        )
    except Exception as e:
        logger.error(f"Failed to update value list: {e}")



if __name__ == "__main__":
    ats = AutomationServer.from_environment()

    workqueue = ats.workqueue()

    # Initialize external systems for automation here..
    Nexuscredentials = Credential.get_credential("KMD Nexus - produktion")
    Afregningscredentials = Credential.get_credential("Odense SQL Server")
    #XFlowcredentials_test = Credential.get_credential("Xflow - test")
    XFlowcredentials_prod = Credential.get_credential("Xflow - produktion")
    

    nexusklient = NexusClient(
        client_id=Nexuscredentials.username,
        client_secret=Nexuscredentials.password,
        instance=Nexuscredentials.data["instance"]
    )

    nexus_organisationer = OrganisationerClient(nexus_client=nexusklient)

    afregningsklient = Tracker(
        username=Afregningscredentials.username,
        password=Afregningscredentials.password,
    )

    xflowklient = XFlowClient(
        instance=XFlowcredentials_prod.data["instance"],
        token=XFlowcredentials_prod.password
    )
    værdilisteklient = ValueListClient(
        client=xflowklient,
    )

    # asyncio.run(opdater_organisationer_i_XFlow())

    # asyncio.run(opdater_leverandører_i_XFlow())

    asyncio.run(opdater_organisationsleverandører_i_XFlow())

    afregningsklient.track_task(
        process_name=procesnavn,
        )

