from wuxia.db import get_db
import docker
from docker.errors import ImageNotFound


client = docker.from_env()


def check_docker_images(image_name='validator:1', path='.', dockerfile='Dockerfile'):
    image = None
    try:
        image = client.images.get(image_name)
    except ImageNotFound:
        image = client.images.build(path=path, tag=image_name, rm=True, dockerfile=dockerfile)
    finally:
        return image


class Validator:
    def __init__(self, challenge_id, user_id):
        db = get_db()
        self.challenge_id = challenge_id
        self.user_id = user_id
        self.image = check_docker_images()
        self.verifiers = db.get_challenge_files(challenge_id, file_types=['verifier'], columns=['file_name'])
        self.results = db.get_challenge_files(challenge_id, file_types=['result'], columns=['file_name'])

    # TODO: generate output from user code with JSONs and compare to expected output text
