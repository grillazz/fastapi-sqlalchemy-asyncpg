import pytest
from apscheduler import ConflictPolicy
from apscheduler.triggers.interval import IntervalTrigger

import app.services.scheduler as scheduler_service


@pytest.mark.anyio
async def test_scheduler_lifespan_starts_and_stops_scheduler(monkeypatch) -> None:
    events = []
    data_store = object()
    event_broker = object()

    class SchedulerStub:
        async def __aenter__(self):
            events.append("enter")
            return self

        async def __aexit__(self, *_args: object) -> None:
            events.append("exit")

        async def add_schedule(
            self, func, trigger, *, id: str, conflict_policy: ConflictPolicy
        ) -> None:
            events.append(("schedule", func, trigger, id, conflict_policy))

        async def start_in_background(self) -> None:
            events.append("start")

    scheduler = SchedulerStub()

    def create_data_store(actual_engine, *, schema):
        assert actual_engine is scheduler_service.engine
        assert schema == "scheduler"
        return data_store

    def create_event_broker(*, client_or_url):
        assert client_or_url == (
            scheduler_service.global_settings.redis_url.unicode_string()
        )
        return event_broker

    def create_scheduler(actual_data_store, actual_event_broker):
        assert actual_data_store is data_store
        assert actual_event_broker is event_broker
        return scheduler

    monkeypatch.setattr(scheduler_service, "SQLAlchemyDataStore", create_data_store)
    monkeypatch.setattr(scheduler_service, "RedisEventBroker", create_event_broker)
    monkeypatch.setattr(scheduler_service, "AsyncScheduler", create_scheduler)

    async with scheduler_service.scheduler_lifespan():
        assert events[0] == "enter"
        event_type, func, trigger, schedule_id, conflict_policy = events[1]
        assert event_type == "schedule"
        assert func is scheduler_service.tick
        assert isinstance(trigger, IntervalTrigger)
        assert schedule_id == "tick-sql-25"
        assert conflict_policy is ConflictPolicy.replace
        assert events[2:] == ["start"]

    assert events[-1] == "exit"
