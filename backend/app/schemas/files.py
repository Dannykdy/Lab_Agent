from pydantic import BaseModel

class FileResponse(BaseModel):
    filename: str
    filesize: str
    diskname: str
    url: str
