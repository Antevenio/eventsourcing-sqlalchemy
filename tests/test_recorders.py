from uuid import uuid4

from eventsourcing.persistence import StoredEvent, Tracking
from eventsourcing.tests.ramdisk import tmpfile_uris

from eventsourcing_sqlalchemy.datastore import SQLAlchemyDatastore
from eventsourcing_sqlalchemy.recorders import (
    SQLAlchemyAggregateRecorder,
    SQLAlchemyApplicationRecorder,
    SQLAlchemyProcessRecorder,
)


from eventsourcing.tests.aggregaterecorder_testcase import (
    AggregateRecorderTestCase,
)
from eventsourcing.tests.applicationrecorder_testcase import (
    ApplicationRecorderTestCase,
)
from eventsourcing.tests.processrecorder_testcase import ProcessRecorderTestCase


class TestSQLAlchemyAggregateRecorder(AggregateRecorderTestCase):
    def setUp(self) -> None:
        self.datastore = SQLAlchemyDatastore("sqlite:///:memory:")

    def create_recorder(self):
        recorder = SQLAlchemyAggregateRecorder(
            datastore=self.datastore, events_table_name="stored_events"
        )
        recorder.create_table()
        return recorder

    def test_insert_and_select(self):
        super(TestSQLAlchemyAggregateRecorder, self).test_insert_and_select()


class TestSQLAlchemySnapshotRecorder(AggregateRecorderTestCase):
    def setUp(self) -> None:
        self.datastore = SQLAlchemyDatastore("sqlite:///:memory:")

    def create_recorder(self):
        recorder = SQLAlchemyAggregateRecorder(
            datastore=self.datastore, events_table_name="snapshots", for_snapshots=True
        )
        recorder.create_table()
        return recorder


class TestSQLAlchemyApplicationRecorder(ApplicationRecorderTestCase):
    def setUp(self) -> None:
        self.datastore = SQLAlchemyDatastore("sqlite:///:memory:?cache=shared")

    def create_recorder(self):
        recorder = SQLAlchemyApplicationRecorder(
            datastore=self.datastore, events_table_name="stored_events"
        )
        recorder.create_table()
        return recorder

    def test_insert_select(self):
        super().test_insert_select()

    def test_concurrent_no_conflicts_sqlite_filedb(self):
        uris = tmpfile_uris()
        db_uri = next(uris)
        db_uri = db_uri.lstrip("file:")
        db_url = f"sqlite:///{db_uri}"
        self.datastore = SQLAlchemyDatastore(url=db_url)
        self.assertTrue(self.datastore.is_sqlite_wal_mode)
        self.assertFalse(self.datastore.access_lock)
        super().test_concurrent_no_conflicts()

    def test_concurrent_no_conflicts(self):
        self.assertFalse(self.datastore.is_sqlite_wal_mode)
        self.assertTrue(self.datastore.access_lock)
        super().test_concurrent_no_conflicts()


class TestSQLAlchemyProcessRecorder(ProcessRecorderTestCase):
    def setUp(self) -> None:
        self.datastore = SQLAlchemyDatastore("sqlite:///:memory:")

    def create_recorder(self):
        recorder = SQLAlchemyProcessRecorder(datastore=self.datastore, events_table_name="stored_events",
                                             tracking_table_name="tracking", )
        recorder.create_table()
        return recorder

    def test_performance(self):
        super().test_performance()

    def test_max_tracking_id_query_should_be_filtered_by_application_name(self):
        recorder = self.create_recorder()
        self.assertEqual(
            recorder.max_tracking_id("upstream_app1"),
            0,
        )
        self.assertEqual(
            recorder.max_tracking_id("upstream_app2"),
            0,
        )

        originator_id1 = uuid4()

        stored_event1 = StoredEvent(
            originator_id=originator_id1,
            originator_version=1,
            topic="topic1",
            state=b"state1",
        )
        tracking1 = Tracking(
            application_name="upstream_app1",
            notification_id=1,
        )

        recorder.insert_events(
            stored_events=[
                stored_event1,
            ],
            tracking=tracking1,
        )

        self.assertEqual(
            recorder.max_tracking_id("upstream_app1"),
            1,
        )
        self.assertEqual(
            recorder.max_tracking_id("upstream_app2"),
            0,
        )


del AggregateRecorderTestCase
del ApplicationRecorderTestCase
del ProcessRecorderTestCase
