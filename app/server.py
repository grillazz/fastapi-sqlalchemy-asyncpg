from granian import Granian


def startup():
    print("Server starting up...")

def shutdown():
    print("Server shutting down...")

server = Granian(
    "main:app",
    host="0.0.0.0",  # Bind to all interfaces
    port=8000,
    workers=4,
    interface="asgi",
    blocking_threads=8  # Optional: threads per worker for blocking ops
)
server.on_startup(startup)
server.on_shutdown(shutdown)
server.serve_forever()
