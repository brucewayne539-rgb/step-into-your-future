STEP INTO YOUR FUTURE — TODAY!
SHAREABLE TEACHER DEMO

WHAT THIS VERSION DOES
- Runs as a normal website when deployed to a web host.
- Teachers receive ONE web link and a teacher access code.
- Teachers do NOT see or enter the OpenAI API key.
- The OpenAI API key is stored as a private server environment variable.
- Default limit: 2 AI portraits per browser session to help control API costs.
- Keeps the expanded 35-career menu and rich colorful Roadmap to Success.
- Photos are processed for generation and are not intentionally written to a student database by this app.

IMPORTANT
This ZIP makes the project DEPLOYMENT-READY; it does not itself create a public internet address.
A web-hosting account must deploy these files. A school/IT review is recommended before student use.

SERVER ENVIRONMENT VARIABLES
OPENAI_API_KEY = your current API key (never put it in the code or share it with teachers)
DEMO_ACCESS_CODE = a short private code you give to teachers
SECRET_KEY = a long random value used to protect sessions
MAX_GENERATIONS_PER_SESSION = 2 (change if desired)

RENDER-READY
A render.yaml file is included. After these files are placed in a Git repository, Render can use it to create a web service. Add OPENAI_API_KEY and DEMO_ACCESS_CODE as private environment variables.

OTHER HOSTS
Any Python host that can run Gunicorn can use:
  pip install -r requirements.txt
  gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 180

LOCAL TESTING
START_APP.bat still works on Windows. If OPENAI_API_KEY is not set on the server/environment, the local version can use the key saved in the local Windows profile as before.

SCHOOL ROLLOUT
Before giving this to students, add district-approved authentication/consent, formal privacy/data-retention language, accessibility review, counselor-vetted career content, admin spending controls, and district IT/security review.
