from pathlib import Path
import pandas as pd

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.annotate_candidates import propose_intent


BASE_DIR = Path(__file__).resolve().parent.parent

# Vercel serverless functions have a read-only application filesystem.
# /tmp is writable during the lifetime of the function instance.
if Path("/tmp").exists():
    UPLOAD_DIR = Path("/tmp") / "ai-text-annotation-uploads"
else:
    UPLOAD_DIR = BASE_DIR / "data" / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(
    directory=str(BASE_DIR / "web" / "templates")
)

app = FastAPI(
    title="Customer Support AI Annotation & QA Platform",
    version="1.0.0",
)
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "web" / "static")),
    name="static",
)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "metrics": {
                "total": 300,
                "matches": 184,
                "mismatches": 0,
                "uncertain": 116,
                "human_review": 116,
            }
        },
    )


@app.get("/review", response_class=HTMLResponse)
async def review_queue(request: Request):
    candidates_path = BASE_DIR / "data" / "annotation" / "annotation_candidates.csv"
    required_columns = [
        "record_id",
        "instruction",
        "source_intent",
        "proposed_intent",
        "proposal_confidence",
        "requires_human_review",
        "proposal_notes",
    ]
    records = []

    if candidates_path.is_file():
        candidates = pd.read_csv(candidates_path, dtype=str).fillna("")
        if set(required_columns).issubset(candidates.columns):
            review_rows = candidates.loc[
                candidates["requires_human_review"].str.upper() == "TRUE",
                required_columns,
            ]
            records = review_rows.to_dict(orient="records")

    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={"records": records},
    )


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="upload.html",
        context={
            "error": None,
            "success": None,
            "preview": None,
            "total": None,
            "annotated": None,
            "uncertain": None,
            "human_review": None,
            "text_column": None,
            "output_file": None,
        },
    )


@app.post("/upload", response_class=HTMLResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...)
):

    try:

        if not file.filename:
            raise ValueError("No file was selected.")

        extension = Path(file.filename).suffix.lower()

        if extension not in {".csv", ".xlsx", ".xls"}:
            raise ValueError(
                "Unsupported file type. Please upload CSV, XLSX, or XLS."
            )

        # Save uploaded file
        safe_name = Path(file.filename).name
        input_path = UPLOAD_DIR / safe_name

        contents = await file.read()

        if not contents:
            raise ValueError("The uploaded file is empty.")

        input_path.write_bytes(contents)

        # Read dataset
        if extension == ".csv":
            df = pd.read_csv(input_path, dtype=str).fillna("")
        else:
            df = pd.read_excel(input_path, dtype=str).fillna("")

        if df.empty:
            raise ValueError("The uploaded dataset contains no records.")

        # Find complaint/text column
        possible_columns = [
            "instruction",
            "complaint",
            "complaints",
            "text",
            "message",
            "customer_complaint",
            "customer_message",
            "query",
            "description",
        ]

        text_column = None

        for column in possible_columns:
            if column in df.columns:
                text_column = column
                break

        # Fallback to first text column
        if text_column is None:

            text_columns = df.select_dtypes(
                include=["object"]
            ).columns.tolist()

            if text_columns:
                text_column = text_columns[0]

        if text_column is None:
            raise ValueError(
                "No text/complaint column could be detected."
            )

        # Run existing annotation engine
        results = []

        for index, row in df.iterrows():

            text = str(row[text_column]).strip()

            if not text:
                proposed = "UNCERTAIN"
                confidence = 0.0
                review_required = "TRUE"
                notes = "Empty complaint text."

            else:

                (
                    proposed,
                    confidence,
                    review_required,
                    notes,
                ) = propose_intent(text)

            results.append(
                {
                    "record_id": index + 1,
                    "instruction": text,
                    "proposed_intent": proposed,
                    "proposal_confidence": confidence,
                    "requires_human_review": review_required,
                    "proposal_notes": notes,
                }
            )

        result_df = pd.DataFrame(results)

        # Save annotated dataset
        output_name = (
            input_path.stem + "_annotated.csv"
        )

        output_path = UPLOAD_DIR / output_name

        result_df.to_csv(
            output_path,
            index=False,
        )

        total = len(result_df)

        uncertain = int(
            (result_df["proposed_intent"] == "UNCERTAIN").sum()
        )

        human_review = int(
            (
                result_df["requires_human_review"] == "TRUE"
            ).sum()
        )

        annotated = total - uncertain

        preview = result_df.head(20).to_dict(
            orient="records"
        )

        return templates.TemplateResponse(
            request=request,
            name="upload.html",
            context={
                "error": None,
                "success": f"Successfully processed {total} records.",
                "preview": preview,
                "total": total,
                "annotated": annotated,
                "uncertain": uncertain,
                "human_review": human_review,
                "text_column": text_column,
                "output_file": output_name,
            },
        )

    except Exception as e:

        return templates.TemplateResponse(
            request=request,
            name="upload.html",
            context={
                "error": str(e),
                "success": None,
                "preview": None,
                "total": None,
                "annotated": None,
                "uncertain": None,
                "human_review": None,
                "text_column": None,
                "output_file": None,
            },
            status_code=500,
        )


@app.get("/download/{filename}")
async def download_file(filename: str):

    file_path = UPLOAD_DIR / Path(filename).name

    if not file_path.exists():
        return {"error": "File not found."}

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="text/csv",
    )