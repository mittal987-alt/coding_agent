class SnapshotManager:

    def __init__(

        self,

        storage,

        integrity,

    ):

        self.storage = storage

        self.integrity = integrity

    async def create(

        self,

        workspace,

        execution_id,

    ):

        ...

    async def restore(

        self,

        snapshot_id,

    ):

        ...