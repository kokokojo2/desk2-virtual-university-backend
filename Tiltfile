watch_file('./deploy/api.env')

# declare docker-compose
docker_compose("./deploy/docker-compose.yaml")

# desk2 backend
docker_build(
    'desk2-api',
    context='.',
    dockerfile='./deploy/api.dockerfile',
    only=['./api/'],
    live_update=[
        sync('./api/', '/app/'),
        run(
            'pip install -r /app/requirements.txt',
            trigger=['./api/requirements.txt']
        ),
        restart_container()
    ]
)