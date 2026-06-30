# CodeXray - GitHub Repository Analyzer
Paste any public GitHub reposiory link and get detailed insights on the maintainability gaps, architectural bottlenecks and risky code files based on a static analysis using 8+ software engineering metrics, supported with AI based root causes and recomendations for highest risk files.

## Features:
- Supports 7+ source file types including Python, C, C++, JavaScript
- Computes 8+ software engineering metrics including maintainability index, git statistics, cyclomatic complexity, duplicate code detection, dead/unused code and circular dependencies if any
- Visualises a file dependency graph representing imported functions or files
- Provides AI insights for riskiest files
- Computes weighted scores and gives overall code health, architectural score and risk level

Access the project here : https://repo-analyzer-zeta.vercel.app

## Run Frontend
npm run dev

## Run backend
uvicorn main:app --reload

## Images
<img width="1132" height="556" alt="image" src="https://github.com/user-attachments/assets/1b0f56b4-8190-4a2c-8d16-e109c1ba8fb5" />
<img width="1365" height="578" alt="image" src="https://github.com/user-attachments/assets/d9ec1389-bf4c-41df-a8fc-a462f1e946b5" />
<img width="1365" height="333" alt="image" src="https://github.com/user-attachments/assets/c307f651-e3bf-42c6-a2dd-9d17b5af8c2a" />
<img width="1365" height="592" alt="image" src="https://github.com/user-attachments/assets/43027065-e8e8-43f2-914b-0cc7d238f858" />
<img width="1069" height="598" alt="image" src="https://github.com/user-attachments/assets/ddd0085d-d59f-4b26-8655-c7ed8f51b4d4" />
<img width="1043" height="597" alt="image" src="https://github.com/user-attachments/assets/e683a7e2-5b63-4a14-82d5-c3b979f8e7e3" />
<img width="1071" height="595" alt="image" src="https://github.com/user-attachments/assets/3ee2bd10-8175-40a5-8e34-a071e10db0e6" />
