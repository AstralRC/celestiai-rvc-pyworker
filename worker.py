"""Vast Serverless PyWorker for the CelestiAI real-time voice changer.

Each worker runs the CelestiAI RVC server on 127.0.0.1:8000 (started by the image's boot
script). Live audio does not pass through this PyWorker: the CelestiAI app opens a Vast
*session* per live user, which reserves this worker's capacity so the autoscaler adds GPUs
as active users grow, and the browser then streams audio to the worker over its own HTTPS
tunnel. The RVC server ends the session when the user disconnects.

Capacity is measured in live users: the RVC server's /vast/bench converts real audio and
pads to real time, so a worker that keeps up reports 1.0 (one user, max_sessions=1) and a
slower one less. The app charges each live user 1.0, so with the endpoint's target
utilisation the autoscaler keeps a spare worker ahead of demand.
"""
from vastai import BenchmarkConfig, HandlerConfig, LogActionConfig, Worker, WorkerConfig

BENCH_SECONDS = 6.0

worker_config = WorkerConfig(
    model_server_url="http://127.0.0.1",
    model_server_port=8000,
    model_log_file="/var/log/rvc/server.log",
    model_healthcheck_url="/health",
    # One live user per GPU keeps audio clean (measured on an RTX 3090 with index files).
    max_sessions=1,
    handlers=[
        HandlerConfig(
            route="/vast/bench",
            allow_parallel_requests=False,
            max_queue_time=60.0,
            workload_calculator=lambda payload: float(payload.get("seconds", BENCH_SECONDS)),
            benchmark_config=BenchmarkConfig(dataset=[{"seconds": BENCH_SECONDS}], runs=3, concurrency=1),
        )
    ],
    log_action_config=LogActionConfig(
        on_load=["Application startup complete."],
        on_error=["[fatal]"],
        on_info=["[realtime]"],
    ),
)

Worker(worker_config).run()
