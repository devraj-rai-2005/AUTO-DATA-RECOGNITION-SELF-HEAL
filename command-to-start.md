# Run Commands

# MAKE SURE THAT YOU MAKE .env FROM THE .env.local and make sure that it will be in the backend and in the root.


### Terminal 1: Backend

```powershell
conda activate dev
cd "D:\FRAMEWORK PROJECT\PROJECT 1\backend"
$env:PYTHONPATH="."
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Frontend

```
cd "D:\FRAMEWORK PROJECT\PROJECT 1\frontend"
npm run dev
```

### Terminal 3: Evaluation Suite (Optional)

```
conda activate dev
cd "D:\FRAMEWORK PROJECT\PROJECT 1\backend"
$env:PYTHONPATH="."
python -m evaluation.run_eval
```

### Open Dashboard

```
http://localhost:3000
```
