# celestiai-rvc-pyworker

Vast.ai Serverless PyWorker for the CelestiAI real-time voice changer.

Vast clones this repo onto each worker (`PYWORKER_REPO`) and runs `worker.py`, which:

- waits for the CelestiAI RVC server on `127.0.0.1:8000` to log `Application startup complete.`
- benchmarks the GPU in seconds of audio converted per second (`/vast/bench`)
- accepts one Vast session per worker; each session is one live user

Contains no secrets. The RVC server image and the app live in a private repository.
