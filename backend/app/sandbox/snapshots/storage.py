class SnapshotStorage:

    async def save(

        self,

        snapshot,

    ):

        ...

    async def load(

        self,

        snapshot_id,

    ):

        ...

    async def delete(

        self,

        snapshot_id,

    ):

        ...