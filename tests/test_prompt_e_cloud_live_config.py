from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class PromptECloudLiveConfigTests(unittest.TestCase):
    def test_base_compose_includes_worker_service(self):
        compose_text = (REPO_ROOT / "infra" / "docker-compose.yml").read_text()
        self.assertIn("\n  worker:\n", compose_text)
        self.assertIn("dockerfile: services/worker/Dockerfile", compose_text)

    def test_prod_compose_mounts_htpasswd(self):
        compose_text = (REPO_ROOT / "infra" / "docker-compose.prod.yml").read_text()
        self.assertIn("./nginx/.htpasswd:/etc/nginx/conf.d/.htpasswd:ro", compose_text)

    def test_nginx_uses_live_domain_wiring(self):
        nginx_text = (REPO_ROOT / "infra" / "nginx" / "nginx.conf").read_text()
        self.assertIn("server_name oncovax.live www.oncovax.live;", nginx_text)
        self.assertIn("/etc/letsencrypt/live/oncovax.live/fullchain.pem", nginx_text)
        self.assertIn("/etc/letsencrypt/live/oncovax.live/privkey.pem", nginx_text)


if __name__ == "__main__":
    unittest.main()
