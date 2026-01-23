1. I fixed the production deployment on EasyPanel by making the API container start the web server directly (instead of relying on a startup script that didn’t match the platform’s Docker Compose behavior).
   This change addresses the “Bad Gateway / no logs” situation by ensuring the backend process actually runs and exposes the expected port, so the reverse proxy can reach it.
2. I reduced operational risk by aligning the container startup with a clean multi-service setup (API + Redis + worker), avoiding hidden background processes that can fail silently.
3. I investigated why the app could look “broken without code changes” and identified the deployment entrypoint mismatch as the root cause, which is a common production footgun.
4. Overall, today’s work was focused on stabilizing production and lowering vulnerability to accidental misconfiguration that can take the service down or make it harder to detect issues.
