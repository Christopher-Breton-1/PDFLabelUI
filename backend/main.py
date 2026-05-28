from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.upload import router as upload_router
from routes.annotation import router as annotation_router
from routes.xml import router as xml_router
from routes.pdf import router as pdf_router
from routes.celery import router as celery_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # allow all headers
)

# Register routes
app.include_router(upload_router, prefix="/upload", tags=["Upload"])
app.include_router(annotation_router, prefix="/annotate", tags=["Annotation"])
app.include_router(xml_router,  prefix="/xml", tags=["XML"])
app.include_router(pdf_router,  prefix="/pdf", tags=["PDF"])
app.include_router(celery_router,  prefix="/celery", tags=["Celery"])

@app.get("/")
def root():
    return {"message": "Welcome to the PDF Annotation API!"}

@app.delete("/rmfiles")
def rmfiles():
    import shutil
    from config import SHARED_TMP_UPLOAD_DIR
    for file in SHARED_TMP_UPLOAD_DIR.iterdir():
        if file.is_file():
            file.unlink()
        elif file.is_dir():
            shutil.rmtree(file)
    return {"message": f"All files removed from {SHARED_TMP_UPLOAD_DIR}"}
