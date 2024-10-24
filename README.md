# transcription-fullstack-app

Implementation of an audio transcription fullstack application with Whisper-tiny model from HuggingFace

![Demo](./docs/Transcription.gif)

# tech stack

- Frontend: Typescript (Vite template, lucide, shadcn)
- Backend: Python (FastAPI, Sqlite, Huggingface)

# To start

```
docker compose -f docker-compose-prod.yml build --no-cache
docker compose -f docker-compose-prod.yml up
```

Frontend: localhost:3000
Backend: localhost:8080/docs

# TODO

- Add architecture diagram, design considerations
- Add unit tests
- Frontend: Dynamic website sizing
- Frontend: Improve UI (Add loading wheel when transcribe button is pressed)
- Backend: Improve search results
