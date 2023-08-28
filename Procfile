server: uvicorn server:app --host 0.0.0.0
celery_worker: celery -A worker.app worker -P eventlet --without-gossip --without-mingle --without-heartbeat -Ofair -E --concurrency 1
celery_beat: celery -A worker.app beat
