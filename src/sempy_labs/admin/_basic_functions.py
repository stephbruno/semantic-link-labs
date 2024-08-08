import sempy.fabric as fabric
from typing import Optional, List
from sempy._utils._log import log
import sempy_labs._icons as icons
from sempy.fabric.exceptions import FabricHTTPException


@log
def assign_workspaces_to_capacity(
    source_capacity: str,
    target_capacity: str,
    workspace: Optional[str | List[str]] = None,
):
    """
    Assigns a workspace to a capacity.

    Parameters
    ----------
    source_capacity : str
        The name of the source capacity.
    target_capacity : str
        The name of the target capacity.
    workspace : str | List[str], default=None
        The name of the workspace(s).
        Defaults to None which resolves to migrating all workspaces within the source capacity to the target capacity.
    """

    if isinstance(workspace, str):
        workspace = [workspace]

    dfC = fabric.list_capacities()
    dfC_filt = dfC[dfC["Display Name"] == source_capacity]
    source_capacity_id = dfC_filt["Id"].iloc[0]

    dfC_filt = dfC[dfC["Display Name"] == target_capacity]
    target_capacity_id = dfC_filt["Id"].iloc[0]

    if workspace is None:
        workspaces = fabric.list_workspaces(
            filter=f"capacityId eq '{source_capacity_id.upper()}'"
        )["Name"].values
    else:
        dfW = fabric.list_workspaces()
        workspaces = dfW[dfW["Name"].isin(workspace)]["Name"].values

    request_body = {
        "targetCapacityObjectId": target_capacity_id,
        "workspacesToAssign": workspaces,
    }

    client = fabric.PowerBIRestClient()
    response = client.post(
        "/v1.0/myorg/admin/capacities/AssignWorkspaces",
        json=request_body,
    )

    if response.status_code != 200:
        raise FabricHTTPException(response)
    print(
        f"{icons.green_dot} The workspaces have been assigned to the '{target_capacity}' capacity."
    )
