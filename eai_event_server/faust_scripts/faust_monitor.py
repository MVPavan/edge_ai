from imports import (
    BaseModel, 
    faust,
    Counter, Deque, cast, TP, HTTPStatus,
)


MAX_AVG_HISTORY = 100
MAX_COMMIT_LATENCY_HISTORY = 30
MAX_SEND_LATENCY_HISTORY = 30
MAX_ASSIGNMENT_LATENCY_HISTORY = 30

class FaustMonitor(BaseModel):
        #: Max number of total run time values to keep to build average.
    # max_avg_history: int = MAX_AVG_HISTORY
    # #: Max number of commit latency numbers to keep.
    # max_commit_latency_history: int = MAX_COMMIT_LATENCY_HISTORY
    # #: Max number of send latency numbers to keep.
    # max_send_latency_history: int = MAX_SEND_LATENCY_HISTORY
    # #: Max number of assignment latency numbers to keep.
    # max_assignment_latency_history: int = MAX_ASSIGNMENT_LATENCY_HISTORY
    #: Number of messages currently being processed.
    messages_active: int = 0    
    #: Number of messages processed in total.
    messages_received_total: int = 0
    #: Count of messages received by topic
    messages_received_by_topic: Counter[str] = cast(Counter[str], None)
    #: Number of messages being processed this second.
    messages_s: int = 0
    #: Number of messages sent in total.
    messages_sent: int = 0
    #: Number of messages sent by topic.
    messages_sent_by_topic: Counter[str] = cast(Counter[str], None)
    #: Number of events currently being processed.
    events_active: int = 0
    #: Number of events processed in total.
    events_total: int = 0
    #: Number of events being processed this second.
    events_s: int = 0
    #: Count of events processed by stream
    events_by_stream: Counter[str] = cast(Counter[str], None)
    #: Count of events processed by task
    events_by_task: Counter[str] = cast(Counter[str], None)
    #: Average event runtime over the last second.
    events_runtime_avg: float = 0.0
    #: Deque of run times used for averages
    events_runtime: Deque[float] = cast(Deque[float], None)
    #: Deque of commit latency values
    commit_latency: Deque[float] = cast(Deque[float], None)
    #: Deque of send latency values
    send_latency: Deque[float] = cast(Deque[float], None)
    #: Deque of assignment latency values.
    assignment_latency: Deque[float] = cast(Deque[float], None)
    #: Counter of times a topics buffer was full
    topic_buffer_full: Counter[TP] = cast(Counter[TP], None)
    #: Arbitrary counts added by apps
    metric_counts: Counter[str] = cast(Counter[str], None)
    #: Number of produce operations that ended in error.
    send_errors: int = 0
    #: Number of partition assignments completed.
    assignments_completed: int = 0
    #: Number of partitions assignments that failed.
    assignments_failed: int = 0
    #: Number of rebalances seen by this worker.
    rebalances: int = 0
    #: Deque of previous n rebalance return latencies.
    rebalance_return_latency: Deque[float] = cast(Deque[float], None)
    #: Deque of previous n rebalance end latencies.
    rebalance_end_latency: Deque[float] = cast(Deque[float], None)
    #: Average rebalance return latency.
    rebalance_return_avg: float = 0.0
    #: Average rebalance end latency.
    rebalance_end_avg: float = 0.0
    #: Counter of returned HTTP status codes.
    http_response_codes: Counter[HTTPStatus] = cast(Counter[HTTPStatus], None)
    #: Deque of previous n HTTP request->response latencies.
    http_response_latency: Deque[float] = cast(Deque[float], None)
    #: Average request->response latency.
    http_response_latency_avg: float = 0.0

def populate_monitor_from_app(app:faust.App) -> FaustMonitor:
    faust_monitor = FaustMonitor()
    faust_monitor.messages_active = app.monitor.messages_active
    faust_monitor.messages_received_total = app.monitor.messages_received_total
    faust_monitor.messages_received_by_topic = app.monitor.messages_received_by_topic
    faust_monitor.messages_s = app.monitor.messages_s
    faust_monitor.messages_sent = app.monitor.messages_sent
    faust_monitor.messages_sent_by_topic = app.monitor.messages_sent_by_topic
    faust_monitor.events_active = app.monitor.events_active
    faust_monitor.events_total = app.monitor.events_total
    faust_monitor.events_s = app.monitor.events_s
    faust_monitor.events_runtime_avg = app.monitor.events_runtime_avg
    # faust_monitor.events_runtime = app.monitor.events_runtime
    # faust_monitor.commit_latency = app.monitor.commit_latency
    # faust_monitor.send_latency = app.monitor.send_latency
    faust_monitor.assignment_latency = app.monitor.assignment_latency
    faust_monitor.metric_counts = app.monitor.metric_counts
    faust_monitor.send_errors = app.monitor.send_errors
    faust_monitor.assignments_completed = app.monitor.assignments_completed
    faust_monitor.assignments_failed = app.monitor.assignments_failed
    
    # faust_monitor.events_by_stream = app.monitor.events_by_stream
    # faust_monitor.events_by_task = app.monitor.events_by_task
    # faust_monitor.topic_buffer_full = app.monitor.topic_buffer_full
    # faust_monitor.rebalances = app.monitor.rebalances
    # faust_monitor.rebalance_return_latency = app.monitor.rebalance_return_latency
    # faust_monitor.rebalance_end_latency = app.monitor.rebalance_end_latency
    # faust_monitor.rebalance_return_avg = app.monitor.rebalance_return_avg
    # faust_monitor.rebalance_end_avg = app.monitor.rebalance_end_avg
    # faust_monitor.http_response_codes = app.monitor.http_response_codes
    # faust_monitor.http_response_latency = app.monitor.http_response_latency
    # faust_monitor.http_response_latency_avg = app.monitor.http_response_latency_avg
    return faust_monitor